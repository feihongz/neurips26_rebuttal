import torch
import torch.nn.functional as F


def soft_update(target, source, tau):
    for target_param, param in zip(target.parameters(), source.parameters()):
        target_param.data.copy_(target_param.data * (1.0 - tau) + param.data * tau)


def hard_update(target, source):
    for target_param, param in zip(target.parameters(), source.parameters()):
        target_param.data.copy_(param.data)


def compute_soft_boosted_drifting_v(
    x,
    y,
    adv_matrix,
    temperatures=(0.1, 0.2, 0.5),
    omega=0.05,
    tau=0.1,
    neg_anchors=None,
    adv_neg=None,
):
    bsz, _, action_dim = y.shape
    diff = y - x.unsqueeze(1)
    dist_sq = torch.sum(diff ** 2, dim=-1) / action_dim

    use_actor_neg = neg_anchors is not None and adv_neg is not None
    if use_actor_neg:
        if neg_anchors.shape[0] != bsz or adv_neg.shape[0] != bsz:
            raise ValueError("neg_anchors / adv_neg batch dim must match x")
        if neg_anchors.shape[1] != adv_neg.shape[1]:
            raise ValueError("neg_anchors and adv_neg K_neg must match")

    forces = []
    for temp in temperatures:
        kernel = torch.exp(-dist_sq / (2 * temp ** 2))

        weight_pull = F.softmax(adv_matrix / tau, dim=1) * kernel
        force_pull = torch.sum(weight_pull.unsqueeze(-1) * diff, dim=1)

        if use_actor_neg:
            diff_neg = neg_anchors - x.unsqueeze(1)
            dist_sq_neg = torch.sum(diff_neg ** 2, dim=-1) / action_dim
            kernel_neg = torch.exp(-dist_sq_neg / (2 * temp ** 2))
            weight_push = F.softmax(-adv_neg / tau, dim=1) * kernel_neg * omega
            force_push = torch.sum(weight_push.unsqueeze(-1) * (-diff_neg), dim=1)
        else:
            weight_push = F.softmax(-adv_matrix / tau, dim=1) * kernel * omega
            force_push = torch.sum(weight_push.unsqueeze(-1) * (-diff), dim=1)

        forces.append(force_pull + force_push)

    v = sum(forces) / len(forces)
    v = torch.clamp(v, -0.1, 0.1)
    return v

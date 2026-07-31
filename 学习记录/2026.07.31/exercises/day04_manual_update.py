import torch


def main():
    torch.manual_seed(7)
    features = torch.randn(32, 2)
    target = 3 * features[:, 0] - 2 * features[:, 1] + 1

    weights = torch.zeros(2, requires_grad=True)
    bias = torch.zeros((), requires_grad=True)
    learning_rate = 0.05

    def loss_value():
        prediction = features @ weights + bias
        return ((prediction - target) ** 2).mean()

    loss_before = loss_value()
    loss_before.backward()

    # Parameters are leaves, so update them without building another graph.
    with torch.no_grad():
        weights -= learning_rate * weights.grad
        bias -= learning_rate * bias.grad

    loss_after = loss_value()

    print("loss_before=", loss_before.item())
    print("loss_after=", loss_after.item())
    print("weights_after=", weights)
    print("bias_after=", bias)
    print("loss_decreased=", loss_after.item() < loss_before.item())


if __name__ == "__main__":
    main()

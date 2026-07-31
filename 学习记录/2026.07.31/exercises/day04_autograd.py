import numpy as np
import torch


def manual_gradients(features, prediction, target):
    errors = prediction - target
    batch_size = features.shape[0]
    d_weights = (2 / batch_size) * (features.T @ errors)
    d_bias = 2 * errors.mean()
    return d_weights, d_bias


def main():
    torch.manual_seed(7)
    dtype = torch.float64

    features = torch.randn(32, 2, dtype=dtype)
    target = 3 * features[:, 0] - 2 * features[:, 1] + 1

    weights = torch.zeros(2, dtype=dtype, requires_grad=True)
    bias = torch.zeros((), dtype=dtype, requires_grad=True)

    prediction = features @ weights + bias
    loss = ((prediction - target) ** 2).mean()

    print("weights_requires_grad=", weights.requires_grad)
    print("bias_requires_grad=", bias.requires_grad)
    print("prediction_grad_fn=", type(prediction.grad_fn).__name__)
    print("loss_grad_fn=", type(loss.grad_fn).__name__)
    print("loss_before_backward=", loss.item())
    print("weights_grad_before_backward=", weights.grad)

    loss.backward()

    manual_dw, manual_db = manual_gradients(
        features.detach().numpy(),
        prediction.detach().numpy(),
        target.detach().numpy(),
    )

    print("weights_grad_after_backward=", weights.grad)
    print("bias_grad_after_backward=", bias.grad)
    print("manual_weights_grad=", manual_dw)
    print("manual_bias_grad=", manual_db)
    print("weights_grad_match=", np.allclose(weights.grad.numpy(), manual_dw))
    print("bias_grad_match=", np.allclose(bias.grad.item(), manual_db))

    # Demonstrate accumulation: a second backward adds to the old gradient.
    loss_again = ((features @ weights + bias - target) ** 2).mean()
    loss_again.backward()
    print("weights_grad_after_second_backward=", weights.grad)

    # Clear gradients before the next training step.
    weights.grad.zero_()
    bias.grad.zero_()
    print("weights_grad_after_zero=", weights.grad)
    print("bias_grad_after_zero=", bias.grad)


if __name__ == "__main__":
    main()

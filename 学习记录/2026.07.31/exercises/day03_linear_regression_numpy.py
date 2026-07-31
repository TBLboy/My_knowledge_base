import numpy as np


def predict(x, weight, bias):
    return x * weight + bias


def mse_loss(prediction, target):
    errors = prediction - target
    return np.mean(errors ** 2)


def gradients(x, prediction, target):
    errors = prediction - target
    d_weight = 2 * np.mean(errors * x)
    d_bias = 2 * np.mean(errors)
    return d_weight, d_bias


def main():
    rng = np.random.default_rng(7)

    # Target relationship: y = 3x + 2 + noise.
    x = np.linspace(-2, 2, 100)
    noise = rng.normal(loc=0.0, scale=0.25, size=x.shape)
    target = 3 * x + 2 + noise

    weight = 0.0
    bias = 0.0
    learning_rate = 0.5
    epochs = 500

    initial_loss = mse_loss(predict(x, weight, bias), target)
    print(f"initial_loss={initial_loss:.6f}")

    for epoch in range(1, epochs + 1):
        prediction = predict(x, weight, bias)
        loss = mse_loss(prediction, target)
        d_weight, d_bias = gradients(x, prediction, target)

        weight -= learning_rate * d_weight
        bias -= learning_rate * d_bias

        if epoch == 1 or epoch % 100 == 0:
            print(
                f"epoch={epoch:03d} loss={loss:.6f} "
                f"weight={weight:.4f} bias={bias:.4f}"
            )

    final_prediction = predict(x, weight, bias)
    final_loss = mse_loss(final_prediction, target)
    print(f"final_loss={final_loss:.6f}")
    print(f"learned_weight={weight:.4f}")
    print(f"learned_bias={bias:.4f}")
    print(f"prediction_at_x_0={predict(np.array([0.0]), weight, bias)[0]:.4f}")


if __name__ == "__main__":
    main()

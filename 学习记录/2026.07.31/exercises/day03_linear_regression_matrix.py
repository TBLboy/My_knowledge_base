import numpy as np


def predict(features, weights, bias):
    return features @ weights + bias


def mse_loss(prediction, target):
    return np.mean((prediction - target) ** 2)


def gradients(features, prediction, target):
    errors = prediction - target
    batch_size = features.shape[0]
    d_weights = (2 / batch_size) * (features.T @ errors)
    d_bias = 2 * np.mean(errors)
    return d_weights, d_bias


def main():
    rng = np.random.default_rng(7)
    samples = 200

    # Two input features: y = 3*x1 - 2*x2 + 1 + noise.
    features = rng.normal(size=(samples, 2))
    noise = rng.normal(loc=0.0, scale=0.1, size=samples)
    target = 3 * features[:, 0] - 2 * features[:, 1] + 1 + noise

    weights = np.zeros(2)
    bias = 0.0
    learning_rate = 0.05

    for epoch in range(1, 501):
        prediction = predict(features, weights, bias)
        loss = mse_loss(prediction, target)
        d_weights, d_bias = gradients(features, prediction, target)

        weights -= learning_rate * d_weights
        bias -= learning_rate * d_bias

        if epoch == 1 or epoch % 100 == 0:
            print(
                f"epoch={epoch:03d} loss={loss:.6f} "
                f"weights={weights} bias={bias:.4f}"
            )

    print(f"final_loss={mse_loss(predict(features, weights, bias), target):.6f}")
    print(f"learned_weights={weights}")
    print(f"learned_bias={bias:.4f}")
    print("expected_weights=[3.0, -2.0], expected_bias=1.0")


if __name__ == "__main__":
    main()

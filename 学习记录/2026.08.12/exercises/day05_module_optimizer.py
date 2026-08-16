"""Day 5: nn.Module + optimizer + state_dict save/load."""
from pathlib import Path

import torch
from torch import nn


def make_data(seed=7, samples=100):
    rng = torch.Generator().manual_seed(seed)
    x = torch.linspace(-2.0, 2.0, samples).reshape(-1, 1)
    target = 3.0 * x + 2.0 + torch.randn(samples, 1, generator=rng) * 0.25
    return x, target


def describe_parameters(model):
    for name, parameter in model.named_parameters():
        print(
            f"parameter {name}: shape={tuple(parameter.shape)}, "
            f"requires_grad={parameter.requires_grad}"
        )


def train(model, x, target, epochs=500, learning_rate=0.05):
    loss_fn = nn.MSELoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)
    initial_loss = loss_fn(model(x), target)
    print(f"initial_loss={initial_loss.item():.6f}")

    for epoch in range(1, epochs + 1):
        optimizer.zero_grad()
        loss = loss_fn(model(x), target)
        loss.backward()
        optimizer.step()
        if epoch == 1 or epoch % 100 == 0:
            print(f"epoch={epoch:03d} loss={loss.item():.6f}")

    final_loss = loss_fn(model(x), target)
    print(f"final_loss={final_loss.item():.6f}")
    return initial_loss.item(), final_loss.item()


def main():
    torch.manual_seed(7)
    model = nn.Linear(1, 1)
    x, target = make_data()

    print("model=", model)
    describe_parameters(model)
    initial_loss, final_loss = train(model, x, target)

    print(f"learned_weight={model.weight.item():.4f}")
    print(f"learned_bias={model.bias.item():.4f}")

    results_dir = Path(__file__).resolve().parents[1] / "results"
    results_dir.mkdir(exist_ok=True)
    checkpoint_path = results_dir / "day05_state_dict.pt"
    torch.save(model.state_dict(), checkpoint_path)
    print(f"checkpoint={checkpoint_path}")

    loaded_model = nn.Linear(1, 1)
    loaded_model.load_state_dict(torch.load(checkpoint_path, weights_only=True))
    original_prediction = model(x)
    loaded_prediction = loaded_model(x)
    match = torch.equal(original_prediction, loaded_prediction)
    print("loaded_prediction_matches=", match)

    print(f"initial_loss={initial_loss:.6f}")
    print(f"final_loss={final_loss:.6f}")


if __name__ == "__main__":
    main()

import torch
from torch import nn


def describe(name, value):
    print(
        f"{name}: shape={tuple(value.shape)}, "
        f"dtype={value.dtype}, device={value.device}"
    )


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(7)

    # One linear layer maps 128 input features to 7 output features.
    layer = nn.Linear(128, 7).to(device)
    print("weight shape=", tuple(layer.weight.shape))
    print("bias shape=", tuple(layer.bias.shape))

    batch_features = torch.randn(32, 128, device=device)
    batch_output = layer(batch_features)
    describe("batch_features", batch_features)
    describe("batch_output", batch_output)

    # Linear applies the same feature mapping to every time step.
    sequence_features = torch.randn(32, 10, 128, device=device)
    sequence_output = layer(sequence_features)
    describe("sequence_features", sequence_features)
    describe("sequence_output", sequence_output)

    # The layer computes x @ weight.T + bias.
    manual_output = batch_features @ layer.weight.T + layer.bias
    print(
        "manual_and_layer_match=",
        torch.allclose(manual_output, batch_output),
    )

    # Each batch and time step keeps its own data; only the last feature
    # dimension is transformed from 128 to 7.
    print("mapping= [B, T, 128] -> [B, T, 7]")


if __name__ == "__main__":
    main()

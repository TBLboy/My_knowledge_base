from pathlib import Path

import torch


def describe(name, value):
    print(
        f"{name}: shape={tuple(value.shape)}, "
        f"dtype={value.dtype}, device={value.device}, "
        f"numel={value.numel()}"
    )


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"torch={torch.__version__}")
    print(f"cuda_available={torch.cuda.is_available()}")
    print(f"device={device}")
    if torch.cuda.is_available():
        print(f"gpu={torch.cuda.get_device_name(0)}")

    scalar = torch.tensor(3.0, dtype=torch.float32, device=device)
    vector = torch.tensor([1, 2, 3], dtype=torch.int64, device=device)
    matrix = torch.arange(12, dtype=torch.float32, device=device).reshape(3, 4)
    image_batch = torch.randn(32, 3, 224, 224, device=device)

    describe("scalar", scalar)
    describe("vector", vector)
    describe("matrix", matrix)
    describe("image_batch", image_batch)

    print("matrix[1, 2]=", matrix[1, 2].item())
    print("matrix[:, 1]=", matrix[:, 1])
    print("matrix.T shape=", tuple(matrix.T.shape))
    print("matrix.reshape(4, 3) shape=", tuple(matrix.reshape(4, 3).shape))
    print("image_batch_mean=", image_batch.mean().item())
    print("image_batch_std=", image_batch.std().item())

    left = torch.randn(2, 3, device=device)
    right = torch.randn(3, 4, device=device)
    product = left @ right
    describe("left @ right", product)

    bias = torch.tensor([1.0, 2.0, 3.0, 4.0], device=device)
    describe("product + bias", product + bias)

    # This is an intentional failure: CPU and CUDA tensors cannot be mixed.
    try:
        cpu_value = torch.tensor([1.0])
        _ = cpu_value + scalar
    except RuntimeError as exc:
        print("expected_device_error=", str(exc).splitlines()[0])

    output_dir = Path(__file__).resolve().parents[1] / "results"
    output_dir.mkdir(exist_ok=True)
    print(f"results_dir={output_dir}")


if __name__ == "__main__":
    main()

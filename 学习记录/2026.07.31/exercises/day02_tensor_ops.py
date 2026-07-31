import torch


def show(name, value):
    print(f"{name}: shape={tuple(value.shape)}, value=\n{value}")


def try_operation(name, operation):
    try:
        result = operation()
        show(name, result)
    except (RuntimeError, TypeError) as exc:
        print(f"{name}: expected_error={str(exc).splitlines()[0]}")


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"torch={torch.__version__}")
    print(f"device={device}")

    matrix = torch.tensor(
        [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
        device=device,
    )
    vector = torch.tensor([10.0, 20.0, 30.0], device=device)
    column = torch.tensor([[10.0], [20.0]], device=device)

    show("matrix", matrix)
    show("vector", vector)
    show("column", column)

    show("matrix + vector", matrix + vector)
    show("matrix * vector", matrix * vector)
    show("matrix + column", matrix + column)

    left = torch.tensor(
        [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
        device=device,
    )
    right = torch.tensor(
        [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]],
        device=device,
    )
    show("left @ right", left @ right)
    show("torch.matmul(left, right)", torch.matmul(left, right))

    try_operation("matrix @ vector", lambda: matrix @ vector)
    try_operation("matrix @ column", lambda: matrix @ column)
    try_operation("matrix + wrong_vector", lambda: matrix + torch.tensor([1.0, 2.0], device=device))

    batch = torch.arange(24, dtype=torch.float32, device=device).reshape(2, 3, 4)
    weights = torch.ones(4, 5, device=device)
    output = batch @ weights
    show("batch", batch)
    show("batch @ weights", output)

    print("\nshape_questions:")
    print("[2, 3] + [3] -> [2, 3]")
    print("[2, 3] @ [3, 4] -> [2, 4]")
    print("[2, 3, 4] @ [4, 5] -> [2, 3, 5]")


if __name__ == "__main__":
    main()

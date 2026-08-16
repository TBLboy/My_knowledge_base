from pathlib import Path

import torch
from torch import nn

def make_data(seed=7, samples=100):
    rng = torch.Generator().manual_seed(seed)
    x = torch.linspace(-2, 2, samples, generator=rng).reshape(-1, 1)
    target = 3.0 * x + 2.0 + torch.randn(samples, generator=rng)*0.25
    return x, target

def describe_parameters(model):
    for name, param in model.named_parameters():
        print(f"parameter {name}: shape={tuple(param.shape)}",
              f"requires_grad={param.requires_grad}")


def main():
    torch.manual_seed(7) # 手动设置随机种子
    model = nn.Linear(1,1)  # 定义线性模型
    x, target = make_data() # 生成数据

    print(f"model={model}") # 打印模型
    describe_parameters(model) # 打印模型参数
    initial_loss, final_loss = train(model, x, target) # 训练模型
    print(f"initial_loss={initial_loss}, final_loss={final_loss}") # 打印训练结果
    print(f"learned_weight={model.weight.item()}, learned_bias={model.bias.item()}") # 打印学习到的参数

    results_dir = Path(__file__).resolve().parent[1] / "results"  # 定义结果目录
    results_dir.mkdir(exist_ok=True)  # 创建结果目录
    checkpoint_path = results_dir / "day05_checkpoint.pth"  # 定义检查点路径
    torch.save(model.state_dict(), checkpoint_path)  # 保存模型状态
    print(f"checkpoint saved to {checkpoint_path}")  # 打印保存路径

    loaded_model = nn.Linear(1, 1)  # 定义加载的模型
    loaded_model.load_state_dict(torch.load(checkpoint_path))  # 加载模型状态
    original_prediction = model(x)  # 原始模型预测
    loaded_prediction = loaded_model(x)  # 加载模型预测
    match = torch.equal(original_prediction, loaded_prediction)  # 比较预测结果
    print(f"match={match}")  # 打印比较结果

    print(f"final_loss={final_loss}")
    print(f"initial_loss={initial_loss}")

if __name__ == "__main__":
    main()

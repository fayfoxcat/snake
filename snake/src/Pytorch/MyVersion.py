import torch
import torchvision

# 加载预训练的ResNet18模型，使用ImageNet1K的权重
model = torchvision.models.resnet18(weights=torchvision.models.resnet.ResNet18_Weights.IMAGENET1K_V1)

# 创建一批随机的图像数据，形状为(1, 3, 64, 64)，
# 这代表1张图像，每张图像有3个颜色通道（红、绿、蓝），每个通道的尺寸为64x64像素
data = torch.rand(1, 3, 64, 64)

labels = torch.rand(1, 1000)  # 创建随机的标签数据，形状为(1, 1000)，这里的1000个标签对应于ImageNet的1000个类别

prediction = model(data)  # 将随机的图像数据输入给模型，得到预测结果

loss = (prediction - labels).sum()
loss.backward() # backward pass
optim = torch.optim.SGD(model.parameters(), lr=1e-2, momentum=0.9)
step = optim.step()


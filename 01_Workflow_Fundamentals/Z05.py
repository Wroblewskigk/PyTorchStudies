"""
Exercise 5: Saving and Loading a Model

- Save your trained model's state_dict() to file.
- Create a new instance of your model class and load the state_dict() you just saved.
- Perform predictions on your test data with the loaded model and confirm they match the
original model predictions.
"""

import torch
from matplotlib import pyplot as plt
from torch import nn

torch.manual_seed(1234)

# Set parameters
# noinspection DuplicatedCode
weight = 0.3
bias = 0.9
num_points = 100

# Create data
X = torch.linspace(0, 1, num_points).unsqueeze(1)
y = weight * X + bias

# Split data
train_split = int(0.8 * len(X))
X_train, y_train = X[:train_split], y[:train_split]
X_test, y_test = X[train_split:], y[train_split:]

# Plot
plt.figure(figsize=(12, 8))
# noinspection DuplicatedCode
plt.scatter(X_train, y_train, label="Train")
plt.scatter(X_test, y_test, label="Test")
plt.legend()
plt.title("Straight Line Data")
plt.show()


class LinearRegressionModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.weight = nn.Parameter(torch.randn(1, requires_grad=True))
        self.bias = nn.Parameter(torch.randn(1, requires_grad=True))

    def forward(self, x):
        return self.weight * x + self.bias


device = "cuda" if torch.cuda.is_available() else "cpu"

model = LinearRegressionModel().to(device)
# noinspection DuplicatedCode
X_train, y_train = X_train.to(device), y_train.to(device)
X_test, y_test = X_test.to(device), y_test.to(device)

loss_fn = nn.L1Loss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

epochs = 300
for epoch in range(epochs):
    model.train()
    y_pred = model(X_train)
    loss = loss_fn(y_pred, y_train)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    if (epoch + 1) % 20 == 0:
        model.eval()
        with torch.inference_mode():
            test_pred = model(X_test)
            test_loss = loss_fn(test_pred, y_test)
        print(f"Epoch {epoch + 1}: Train loss {loss.item():.4f} | Test loss {test_loss.item():.4f}")

model.eval()
with torch.inference_mode():
    predictions = model(X_test).cpu()

plt.figure(figsize=(12, 8))
plt.scatter(X_train.cpu(), y_train.cpu(), label="Train")
plt.scatter(X_test.cpu(), y_test.cpu(), label="Test")
plt.scatter(X_test.cpu(), predictions, label="Predictions", marker="x")
plt.legend()
plt.title("Model Predictions vs. Data")
plt.show()

# Save model
MODEL_PATH = "workflow_model.pth"
torch.save(model.state_dict(), MODEL_PATH)

# Load model and move to the same device
loaded_model = LinearRegressionModel().to(device)
loaded_model.load_state_dict(torch.load(MODEL_PATH, weights_only=True))
loaded_model.eval()

with torch.inference_mode():
    loaded_predictions = loaded_model(X_test)  # X_test is already on device

# Plot loaded model predictions
plt.figure(figsize=(12, 8))
plt.scatter(X_train.cpu(), y_train.cpu(), label="Train")
plt.scatter(X_test.cpu(), y_test.cpu(), label="Test")
plt.scatter(X_test.cpu(), loaded_predictions.cpu(), label="Predictions", marker="x")
plt.legend()
plt.title("Model Predictions vs. Data (Loaded Model)")
plt.show()

# Compare predictions
print(torch.allclose(loaded_predictions.cpu(), predictions))

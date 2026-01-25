"""
CNN model for sunset time prediction from images.
"""

import torch
import torch.nn as nn
import torchvision.models as models


class SunsetPredictor(nn.Module):
    """
    CNN-based model to predict hours until sunset from sky images.
    Uses a pre-trained ResNet backbone with regression head.
    """
    
    def __init__(self, backbone="resnet18", pretrained=True, dropout=0.5):
        """
        Args:
            backbone: Backbone architecture (resnet18, resnet34, resnet50, etc.)
            pretrained: Use pretrained weights
            dropout: Dropout rate
        """
        super(SunsetPredictor, self).__init__()
        
        # Load backbone
        if backbone == "resnet18":
            self.backbone = models.resnet18(pretrained=pretrained)
            num_features = 512
        elif backbone == "resnet34":
            self.backbone = models.resnet34(pretrained=pretrained)
            num_features = 512
        elif backbone == "resnet50":
            self.backbone = models.resnet50(pretrained=pretrained)
            num_features = 2048
        else:
            raise ValueError(f"Unsupported backbone: {backbone}")
        
        # Replace classification head with regression head
        self.backbone.fc = nn.Identity()
        
        # Regression head
        self.regressor = nn.Sequential(
            nn.Linear(num_features, 256),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, 1)  # Predict hours until sunset
        )
    
    def forward(self, x):
        """
        Forward pass.
        
        Args:
            x: Input images (batch_size, 3, H, W)
        
        Returns:
            Predicted hours until sunset (batch_size, 1)
        """
        features = self.backbone(x)
        prediction = self.regressor(features)
        return prediction.squeeze(-1)


class SimpleSunsetCNN(nn.Module):
    """
    Simple CNN model for sunset prediction (lighter alternative).
    """
    
    def __init__(self):
        super(SimpleSunsetCNN, self).__init__()
        
        # Convolutional layers
        self.conv_layers = nn.Sequential(
            # First conv block
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            
            # Second conv block
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            
            # Third conv block
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            
            # Fourth conv block
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            
            # Fifth conv block
            nn.Conv2d(256, 512, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1))
        )
        
        # Regression head
        self.regressor = nn.Sequential(
            nn.Flatten(),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(128, 1)
        )
    
    def forward(self, x):
        features = self.conv_layers(x)
        prediction = self.regressor(features)
        return prediction.squeeze(-1)


def create_model(model_type="resnet18", pretrained=True, **kwargs):
    """
    Factory function to create a model.
    
    Args:
        model_type: Type of model ("resnet18", "resnet34", "resnet50", "simple")
        pretrained: Use pretrained weights (for ResNet models)
        **kwargs: Additional arguments
    
    Returns:
        Model instance
    """
    if model_type == "simple":
        return SimpleSunsetCNN()
    else:
        return SunsetPredictor(backbone=model_type, pretrained=pretrained, **kwargs)


if __name__ == "__main__":
    # Test model
    model = create_model("resnet18", pretrained=True)
    print(f"Model: {model}")
    
    # Test forward pass
    dummy_input = torch.randn(2, 3, 224, 224)
    output = model(dummy_input)
    print(f"Input shape: {dummy_input.shape}")
    print(f"Output shape: {output.shape}")
    print(f"Sample output: {output}")


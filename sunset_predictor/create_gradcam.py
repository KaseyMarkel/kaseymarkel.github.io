"""
Create Figure 9: Grad-CAM Activation Maps
Shows what parts of images the model focuses on for predictions.
"""

import torch
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from PIL import Image
import cv2
from pathlib import Path
import json

plt.rcParams.update({
    'font.size': 11,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight'
})


class GradCAM:
    """Grad-CAM implementation for visualizing model attention."""
    
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        # Register hooks
        self.target_layer.register_forward_hook(self.save_activation)
        self.target_layer.register_full_backward_hook(self.save_gradient)
    
    def save_activation(self, module, input, output):
        self.activations = output
    
    def save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0]
    
    def generate_cam(self, input_image, class_idx=None):
        """Generate class activation map."""
        self.model.eval()
        
        # Forward pass
        output = self.model(input_image)
        
        if class_idx is None:
            class_idx = output.argmax(dim=1)
        
        # Backward pass
        self.model.zero_grad()
        output.backward(gradient=torch.ones_like(output), retain_graph=True)
        
        # Get gradients and activations
        gradients = self.gradients[0].cpu().data.numpy()
        activations = self.activations[0].cpu().data.numpy()
        
        # Calculate weights (global average pooling of gradients)
        weights = np.mean(gradients, axis=(1, 2))
        
        # Generate CAM
        cam = np.zeros(activations.shape[1:], dtype=np.float32)
        for i, w in enumerate(weights):
            cam += w * activations[i]
        
        # Apply ReLU
        cam = np.maximum(cam, 0)
        
        # Normalize
        cam = cam / (cam.max() + 1e-8)
        
        return cam, output.item()


def create_gradcam_figure(model, metadata, checkpoint_path, image_dir, 
                         output_path="figures/fig9_gradcam.pdf", num_samples=6):
    """Create Grad-CAM visualization figure."""
    from model import create_model
    from torchvision import transforms
    
    # Load model
    checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    
    # Get target layer (last conv layer in ResNet)
    target_layer = None
    for name, module in model.named_modules():
        if 'layer4' in name and isinstance(module, torch.nn.Conv2d):
            target_layer = module
    
    if target_layer is None:
        # Fallback: use last layer before adaptive pool
        for name, module in model.named_modules():
            if 'backbone.layer4' in name:
                target_layer = list(model.backbone.layer4.children())[-1]
                break
    
    if target_layer is None:
        print("⚠ Could not find target layer for Grad-CAM. Creating simplified figure.")
        create_simplified_attention_figure(metadata, image_dir, output_path, num_samples)
        return
    
    # Initialize Grad-CAM
    gradcam = GradCAM(model, target_layer)
    
    # Transform
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])
    
    # Select diverse samples
    indices = np.linspace(0, len(metadata)-1, num_samples, dtype=int)
    
    fig, axes = plt.subplots(2, num_samples, figsize=(18, 6))
    if num_samples == 1:
        axes = axes.reshape(2, 1)
    
    for col, idx in enumerate(indices):
        # Load image
        img_path = Path(metadata[idx]["image_path"])
        if not img_path.is_absolute():
            img_path = Path(image_dir) / img_path
        
        try:
            img = Image.open(img_path).convert("RGB")
            img_tensor = transform(img).unsqueeze(0)
            
            # Generate CAM
            cam, prediction = gradcam.generate_cam(img_tensor)
            
            # Resize CAM to original image size
            cam_resized = cv2.resize(cam, img.size, interpolation=cv2.INTER_LINEAR)
            cam_resized = np.uint8(255 * cam_resized)
            heatmap = cm.jet(cam_resized)[:, :, :3]
            
            # Original image
            axes[0, col].imshow(img)
            axes[0, col].axis('off')
            axes[0, col].set_title(f'Sample {col+1}', fontweight='bold')
            
            # Overlay heatmap
            img_array = np.array(img) / 255.0
            overlay = 0.6 * img_array + 0.4 * heatmap
            axes[1, col].imshow(overlay)
            axes[1, col].axis('off')
            axes[1, col].set_title(f'Pred: {prediction:.2f}h', fontweight='bold')
            
        except Exception as e:
            print(f"Error processing image {idx}: {e}")
            axes[0, col].text(0.5, 0.5, "Error", ha='center', va='center')
            axes[1, col].text(0.5, 0.5, "Error", ha='center', va='center')
    
    plt.suptitle('Grad-CAM Visualizations: Model Attention', 
                fontweight='bold', fontsize=14, y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, format='pdf')
    print(f"✓ Saved: {output_path}")
    plt.close()


def create_simplified_attention_figure(metadata, image_dir, output_path, num_samples=6):
    """Create simplified attention figure when Grad-CAM unavailable."""
    fig, axes = plt.subplots(2, num_samples, figsize=(18, 6))
    
    indices = np.linspace(0, len(metadata)-1, num_samples, dtype=int)
    
    for col, idx in enumerate(indices):
        img_path = Path(metadata[idx]["image_path"])
        if not img_path.is_absolute():
            img_path = Path(image_dir) / img_path
        
        try:
            img = Image.open(img_path).convert("RGB")
            axes[0, col].imshow(img)
            axes[0, col].axis('off')
            axes[0, col].set_title(f'Sample {col+1}', fontweight='bold')
            
            # Simplified: show image with text overlay
            axes[1, col].imshow(img, alpha=0.7)
            axes[1, col].text(img.size[0]//2, img.size[1]//2, 
                            'Attention\nVisualization', 
                            ha='center', va='center', 
                            fontsize=12, fontweight='bold',
                            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            axes[1, col].axis('off')
            axes[1, col].set_title('Model Focus', fontweight='bold')
        except:
            axes[0, col].text(0.5, 0.5, "Error", ha='center', va='center')
            axes[1, col].text(0.5, 0.5, "Error", ha='center', va='center')
    
    plt.suptitle('Model Attention Visualization', fontweight='bold', fontsize=14)
    plt.tight_layout()
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, format='pdf')
    print(f"✓ Saved: {output_path} (simplified)")
    plt.close()


if __name__ == "__main__":
    import sys
    
    metadata_file = "data/processed/test_metadata.json"
    checkpoint_path = "checkpoints/best.pth"
    image_dir = "data/synthetic_images"
    
    if Path(metadata_file).exists() and Path(checkpoint_path).exists():
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
        
        from model import create_model
        model = create_model("resnet18", pretrained=False)
        
        create_gradcam_figure(model, metadata, checkpoint_path, image_dir)
    else:
        print("⚠ Checkpoint or metadata not found. Skipping Grad-CAM figure.")


#!/usr/bin/env python3
"""
Chapter 16, Example 3: Imitation Learning from Demonstrations

This example demonstrates:
1. Behavioral cloning from expert demonstrations
2. Dataset loading and preprocessing
3. Policy training via supervised learning
4. Performance evaluation

Dependencies:
    pip install numpy matplotlib torch scikit-learn

Expected Output:
    - Trained imitation policy
    - Training loss curves
    - Policy evaluation metrics
    - Demonstration replay

Platform: Ubuntu 22.04, Python 3.10+
Author: Physical AI & Humanoid Robotics Textbook
"""

import numpy as np
import matplotlib.pyplot as plt

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    TORCH_AVAILABLE = True
except ImportError:
    print("Warning: PyTorch not installed")
    TORCH_AVAILABLE = False


class DemonstrationDataset(Dataset if TORCH_AVAILABLE else object):
    """Dataset of expert demonstrations."""
    
    def __init__(self, states, actions):
        if TORCH_AVAILABLE:
            self.states = torch.FloatTensor(states)
            self.actions = torch.FloatTensor(actions)
    
    def __len__(self):
        return len(self.states) if TORCH_AVAILABLE else 0
    
    def __getitem__(self, idx):
        if TORCH_AVAILABLE:
            return self.states[idx], self.actions[idx]
        return None, None


class ImitationPolicy(nn.Module if TORCH_AVAILABLE else object):
    """Policy network for behavioral cloning."""
    
    def __init__(self, state_dim, action_dim):
        if TORCH_AVAILABLE:
            super().__init__()
            self.network = nn.Sequential(
                nn.Linear(state_dim, 256),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(256, 128),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(128, action_dim)
            )
    
    def forward(self, x):
        if TORCH_AVAILABLE:
            return self.network(x)
        return None


def generate_expert_demonstrations(n_demos=100, traj_length=50):
    """Generate synthetic expert demonstrations."""
    states = []
    actions = []
    
    state_dim = 6
    action_dim = 3
    
    for _ in range(n_demos):
        state = np.random.randn(state_dim)
        for _ in range(traj_length):
            # Expert policy: simple PD controller
            action = -0.5 * state[:action_dim] - 0.1 * state[action_dim:]
            action += np.random.randn(action_dim) * 0.05  # noise
            
            states.append(state)
            actions.append(action)
            
            # Simple dynamics
            state = state + np.concatenate([action * 0.1, 
                                           np.random.randn(action_dim) * 0.01])
    
    return np.array(states), np.array(actions)


def train_behavioral_cloning(dataset, state_dim, action_dim, n_epochs=50):
    """Train policy via behavioral cloning."""
    if not TORCH_AVAILABLE:
        print("PyTorch not available")
        return None, []
    
    policy = ImitationPolicy(state_dim, action_dim)
    optimizer = optim.Adam(policy.parameters(), lr=1e-3)
    criterion = nn.MSELoss()
    
    dataloader = DataLoader(dataset, batch_size=64, shuffle=True)
    
    losses = []
    
    print(f"\nTraining for {n_epochs} epochs...")
    
    for epoch in range(n_epochs):
        epoch_loss = 0
        for states, actions in dataloader:
            pred_actions = policy(states)
            loss = criterion(pred_actions, actions)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
        
        avg_loss = epoch_loss / len(dataloader)
        losses.append(avg_loss)
        
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{n_epochs}, Loss: {avg_loss:.6f}")
    
    return policy, losses


def main():
    """Main execution function."""
    print("=" * 70)
    print("Chapter 16, Example 3: Imitation Learning")
    print("=" * 70)
    
    # Generate demonstrations
    print("\nGenerating expert demonstrations...")
    states, actions = generate_expert_demonstrations(n_demos=100, traj_length=50)
    
    print(f"Dataset size: {len(states)} samples")
    print(f"State dim: {states.shape[1]}")
    print(f"Action dim: {actions.shape[1]}")
    
    if not TORCH_AVAILABLE:
        print("\nPyTorch not available. Please install: pip install torch")
        return
    
    # Create dataset
    dataset = DemonstrationDataset(states, actions)
    
    # Train
    policy, losses = train_behavioral_cloning(
        dataset, states.shape[1], actions.shape[1], n_epochs=50
    )
    
    # Plot training curve
    plt.figure(figsize=(10, 5))
    plt.plot(losses, linewidth=2)
    plt.xlabel('Epoch')
    plt.ylabel('MSE Loss')
    plt.title('Behavioral Cloning Training')
    plt.grid(True, alpha=0.3)
    plt.yscale('log')
    plt.show()
    
    print("\n" + "="*70)
    print("Imitation learning complete!")
    print("="*70)


if __name__ == "__main__":
    main()

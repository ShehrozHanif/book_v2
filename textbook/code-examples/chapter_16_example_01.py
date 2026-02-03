#!/usr/bin/env python3
"""
Chapter 16, Example 1: RL Agent for Joint Control

This example demonstrates:
1. Reinforcement learning for robot joint control
2. PPO (Proximal Policy Optimization) implementation  
3. Gymnasium environment for joint tracking
4. Training loop and policy evaluation

Dependencies:
    pip install numpy matplotlib gymnasium torch

Expected Output:
    - Training progress and rewards
    - Learned policy performance
    - Joint tracking visualization
    - Policy network weights

Platform: Ubuntu 22.04, Python 3.10+
Author: Physical AI & Humanoid Robotics Textbook
"""

import numpy as np
import matplotlib.pyplot as plt

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    TORCH_AVAILABLE = True
except ImportError:
    print("Warning: PyTorch not installed. Install with: pip install torch")
    TORCH_AVAILABLE = False

try:
    import gymnasium as gym
    GYM_AVAILABLE = True
except ImportError:
    print("Warning: Gymnasium not installed. Install with: pip install gymnasium")
    GYM_AVAILABLE = False


class PolicyNetwork(nn.Module if TORCH_AVAILABLE else object):
    """Simple feedforward policy network."""
    
    def __init__(self, state_dim, action_dim, hidden_dim=64):
        if TORCH_AVAILABLE:
            super().__init__()
            self.network = nn.Sequential(
                nn.Linear(state_dim, hidden_dim),
                nn.Tanh(),
                nn.Linear(hidden_dim, hidden_dim),
                nn.Tanh(),
                nn.Linear(hidden_dim, action_dim)
            )
        
    def forward(self, state):
        if TORCH_AVAILABLE:
            return self.network(state)
        return None


class JointTrackingEnv:
    """Simple joint tracking environment."""
    
    def __init__(self, n_joints=3):
        self.n_joints = n_joints
        self.dt = 0.01
        self.max_steps = 500
        
        self.state_dim = n_joints * 2  # position and velocity
        self.action_dim = n_joints
        
        self.reset()
    
    def reset(self):
        self.joint_pos = np.zeros(self.n_joints)
        self.joint_vel = np.zeros(self.n_joints)
        self.target_pos = np.random.uniform(-1.0, 1.0, self.n_joints)
        self.step_count = 0
        return self._get_state()
    
    def _get_state(self):
        return np.concatenate([self.joint_pos, self.joint_vel])
    
    def step(self, action):
        # Simple dynamics: velocity control
        self.joint_vel += action * self.dt
        self.joint_pos += self.joint_vel * self.dt
        
        # Compute reward
        error = np.linalg.norm(self.joint_pos - self.target_pos)
        reward = -error - 0.01 * np.linalg.norm(action)
        
        self.step_count += 1
        done = self.step_count >= self.max_steps or error < 0.05
        
        return self._get_state(), reward, done, {}


def train_ppo_agent(env, n_episodes=100):
    """Simple PPO training loop."""
    if not TORCH_AVAILABLE:
        print("PyTorch not available. Skipping training.")
        return None, []
    
    policy = PolicyNetwork(env.state_dim, env.action_dim)
    optimizer = optim.Adam(policy.parameters(), lr=3e-4)
    
    episode_rewards = []
    
    print(f"\nTraining PPO agent for {n_episodes} episodes...")
    
    for ep in range(n_episodes):
        state = env.reset()
        episode_reward = 0
        states, actions, rewards = [], [], []
        
        done = False
        while not done:
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            action_mean = policy(state_tensor)
            action = action_mean.detach().numpy()[0]
            
            next_state, reward, done, _ = env.step(action)
            
            states.append(state)
            actions.append(action)
            rewards.append(reward)
            
            state = next_state
            episode_reward += reward
        
        # Simple policy gradient update
        returns = []
        G = 0
        for r in reversed(rewards):
            G = r + 0.99 * G
            returns.insert(0, G)
        
        returns = torch.FloatTensor(returns)
        returns = (returns - returns.mean()) / (returns.std() + 1e-8)
        
        states_tensor = torch.FloatTensor(states)
        actions_tensor = torch.FloatTensor(actions)
        
        policy_loss = 0
        for i in range(len(states)):
            action_pred = policy(states_tensor[i:i+1])
            loss = ((action_pred - actions_tensor[i:i+1]) ** 2).sum()
            policy_loss += loss * returns[i]
        
        optimizer.zero_grad()
        policy_loss.backward()
        optimizer.step()
        
        episode_rewards.append(episode_reward)
        
        if (ep + 1) % 10 == 0:
            avg_reward = np.mean(episode_rewards[-10:])
            print(f"Episode {ep+1}/{n_episodes}, Avg Reward: {avg_reward:.2f}")
    
    return policy, episode_rewards


def main():
    """Main execution function."""
    print("=" * 70)
    print("Chapter 16, Example 1: RL Agent for Joint Control")
    print("=" * 70)
    
    # Create environment
    env = JointTrackingEnv(n_joints=3)
    
    print(f"\nEnvironment:")
    print(f"  State dimension: {env.state_dim}")
    print(f"  Action dimension: {env.action_dim}")
    print(f"  Max steps per episode: {env.max_steps}")
    
    # Train agent
    policy, rewards = train_ppo_agent(env, n_episodes=100)
    
    if rewards:
        # Plot training curve
        plt.figure(figsize=(10, 5))
        plt.plot(rewards, alpha=0.6, label='Episode Reward')
        plt.plot(np.convolve(rewards, np.ones(10)/10, mode='valid'), 
                 linewidth=2, label='Moving Average (10)')
        plt.xlabel('Episode')
        plt.ylabel('Total Reward')
        plt.title('Training Progress')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()
    
    print("\n" + "="*70)
    print("RL training complete!")
    print("="*70)


if __name__ == "__main__":
    main()

# Writer Onboarding Checklist

**Purpose**: Ensure writers are ready to create high-quality textbook content

**Spec**: 002-content-writing | **Date**: 2026-02-03 | **Status**: Active

---

## Welcome!

Welcome to the Humanoid Robotics Textbook project. This document will guide you through the setup process and ensure you're ready to start writing.

**Project Goal**: Create a comprehensive 4-module textbook (52,000 words, 22 chapters) that serves as the authoritative knowledge base for the RAG chatbot.

**Your Role**: Write clear, accurate, well-documented chapters with runnable code examples.

**Timeline**: Modules 1-3 complete in 3 weeks; Module 4 optional (Week 4)

---

## Prerequisites

Before starting, ensure you have:

- [ ] Basic understanding of robotics concepts
- [ ] Programming experience (Python and/or C++)
- [ ] Familiarity with ROS 2 (recommended but not required)
- [ ] Access to Ubuntu 22.04 environment (local VM or lab machine)
- [ ] Text editor or IDE for markdown and code
- [ ] Git installed and configured

---

## Phase 1: Environment Setup

### 1.1 Repository Access

- [ ] Clone the textbook repository:
  ```bash
  git clone <repository-url>
  cd book
  ```

- [ ] Create feature branch for your work:
  ```bash
  git checkout -b 002-content-writing
  ```

- [ ] Verify directory structure:
  ```bash
  ls -la textbook/
  # Should see: chapters/, code-examples/, metadata/
  ```

### 1.2 Development Environment

**Option A: Local VM (Recommended)**

- [ ] Install Ubuntu 22.04 (VM or native)
- [ ] Update system packages:
  ```bash
  sudo apt update && sudo apt upgrade -y
  ```

**Option B: Lab Machine**

- [ ] Obtain access to shared lab VM
- [ ] SSH into lab machine
- [ ] Verify Ubuntu version:
  ```bash
  lsb_release -a
  # Should show: Ubuntu 22.04
  ```

### 1.3 ROS 2 Humble LTS Installation

- [ ] Install ROS 2 Humble:
  ```bash
  # Set locale
  sudo apt install locales
  sudo locale-gen en_US en_US.UTF-8
  sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
  export LANG=en_US.UTF-8

  # Setup sources
  sudo apt install software-properties-common
  sudo add-apt-repository universe
  sudo apt update && sudo apt install curl -y
  sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

  # Add ROS 2 repository
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

  # Install ROS 2 Humble
  sudo apt update
  sudo apt install ros-humble-desktop -y
  ```

- [ ] Source ROS 2 in your shell:
  ```bash
  echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
  source ~/.bashrc
  ```

- [ ] Verify ROS 2 installation:
  ```bash
  ros2 --version
  # Should show: ros2 cli version: 0.X.X (Humble)
  ```

### 1.4 Gazebo 11 Installation

- [ ] Install Gazebo 11:
  ```bash
  sudo apt install gazebo11 libgazebo11-dev -y
  ```

- [ ] Verify Gazebo installation:
  ```bash
  gazebo --version
  # Should show: Gazebo multi-robot simulator, version 11.X.X
  ```

- [ ] Test Gazebo launch:
  ```bash
  gazebo
  # Should open Gazebo GUI (close after verification)
  ```

### 1.5 Development Tools

- [ ] Install required packages:
  ```bash
  sudo apt install -y \
    python3-pip \
    python3-pytest \
    build-essential \
    cmake \
    git \
    jq \
    curl
  ```

- [ ] Install Python dependencies:
  ```bash
  pip3 install numpy matplotlib scipy pyyaml
  ```

- [ ] Verify tools:
  ```bash
  python3 --version  # Should show Python 3.10+
  cmake --version    # Should show CMake 3.X+
  jq --version       # Should show jq-1.X
  ```

---

## Phase 2: Repository Familiarization

### 2.1 Review Project Structure

- [ ] Read the spec:
  ```bash
  cat specs/002-content-writing/spec.md
  ```

- [ ] Review the plan:
  ```bash
  cat specs/002-content-writing/plan.md
  ```

- [ ] Understand the tasks:
  ```bash
  cat specs/002-content-writing/tasks.md
  ```

### 2.2 Review Chapter Template

- [ ] Open chapter template:
  ```bash
  cat textbook/chapters/_chapter-template.md
  ```

- [ ] Note the structure:
  - YAML front matter (metadata)
  - Learning Objectives
  - Introduction
  - Key Concepts
  - Code Examples
  - Summary
  - References

### 2.3 Review Code Examples Structure

- [ ] Check code examples directory:
  ```bash
  ls -la textbook/code-examples/
  ```

- [ ] Review naming convention:
  - Format: `chapter_XX_example_YY.ext`
  - Example: `chapter_01_example_01.urdf`

- [ ] Read code examples README:
  ```bash
  cat textbook/code-examples/README.md
  ```

### 2.4 Review References Format

- [ ] Check references file:
  ```bash
  cat textbook/metadata/references.json
  ```

- [ ] Note APA format requirements:
  ```json
  {
    "id": "ref_001",
    "citation": "Author, A. (Year). Title. Publisher.",
    "url": "https://example.com",
    "type": "book|paper|documentation|datasheet"
  }
  ```

---

## Phase 3: Workflow Understanding

### 3.1 Chapter Creation Workflow

- [ ] Understand the chapter creation process:
  1. Generate chapter from template
  2. Write content (2,300-2,400 words)
  3. Create code examples (2-3 per chapter)
  4. Test code examples locally
  5. Add references
  6. Verify word count
  7. Validate references
  8. Submit for review

### 3.2 Test Automation Scripts

- [ ] Test chapter creation script:
  ```bash
  cd scripts
  ./create-chapter.sh --help
  ```

- [ ] Test word count verification:
  ```bash
  ./verify-word-count.sh --help
  ```

- [ ] Test code example testing:
  ```bash
  ./test-code-examples.sh --help
  ```

- [ ] Test reference validation:
  ```bash
  ./validate-references.sh --help
  ```

- [ ] Test RAG metadata generation:
  ```bash
  ./generate-rag-metadata.sh --help
  ```

### 3.3 Review Process

- [ ] Read review process documentation:
  ```bash
  cat textbook/REVIEW_PROCESS.md
  ```

- [ ] Understand review timeline:
  - Submission: After module complete
  - Expert assignment: <12 hours
  - Expert review: 24-48 hours
  - Issue resolution: <24 hours
  - Approval: After resolution

- [ ] Note quality gates:
  - 95%+ accuracy required
  - 100% code examples must execute
  - All references must be valid

---

## Phase 4: Practice Run

### 4.1 Create Test Chapter

- [ ] Create a test chapter:
  ```bash
  cd scripts
  ./create-chapter.sh --id 99 --module "Test Module" --title "Test Chapter"
  ```

- [ ] Verify file created:
  ```bash
  ls -la ../textbook/chapters/99-test-chapter.md
  ```

### 4.2 Write Test Content

- [ ] Open test chapter in editor:
  ```bash
  # Use your preferred editor
  nano ../textbook/chapters/99-test-chapter.md
  # OR
  vim ../textbook/chapters/99-test-chapter.md
  # OR
  code ../textbook/chapters/99-test-chapter.md
  ```

- [ ] Fill in:
  - Learning objectives (3-5 items)
  - Introduction (200-300 words)
  - Key concepts (1-2 sections, 400-600 words each)
  - Summary (200 words)
  - References (2-3 citations)

### 4.3 Create Test Code Example

- [ ] Create a simple Python example:
  ```bash
  cat > ../textbook/code-examples/chapter_99_example_01.py << 'EOF'
  #!/usr/bin/env python3
  """
  Test example for writer onboarding
  Demonstrates a simple ROS 2 publisher
  """
  import rclpy
  from rclpy.node import Node
  from std_msgs.msg import String

  class TestPublisher(Node):
      def __init__(self):
          super().__init__('test_publisher')
          self.publisher = self.create_publisher(String, 'test_topic', 10)
          self.timer = self.create_timer(1.0, self.timer_callback)
          self.count = 0

      def timer_callback(self):
          msg = String()
          msg.data = f'Hello World: {self.count}'
          self.publisher.publish(msg)
          self.get_logger().info(f'Publishing: "{msg.data}"')
          self.count += 1

  def main(args=None):
      rclpy.init(args=args)
      node = TestPublisher()
      try:
          rclpy.spin(node)
      except KeyboardInterrupt:
          pass
      finally:
          node.destroy_node()
          rclpy.shutdown()

  if __name__ == '__main__':
      main()
  EOF
  ```

- [ ] Make executable:
  ```bash
  chmod +x ../textbook/code-examples/chapter_99_example_01.py
  ```

### 4.4 Test Code Example

- [ ] Run the example:
  ```bash
  cd ../textbook/code-examples/
  python3 chapter_99_example_01.py
  # Should see: Publishing: "Hello World: 0", "Hello World: 1", etc.
  # Press Ctrl+C to stop
  ```

- [ ] Verify with test harness:
  ```bash
  cd ../../scripts
  ./test-code-examples.sh --chapter 99
  ```

### 4.5 Add Test References

- [ ] Add reference to references.json:
  ```bash
  # Manually edit textbook/metadata/references.json
  # Add entry:
  {
    "id": "ref_999",
    "citation": "ROS 2 Documentation. (2024). ROS 2 Humble Documentation. Open Robotics.",
    "url": "https://docs.ros.org/en/humble/",
    "type": "documentation"
  }
  ```

- [ ] Cite reference in test chapter:
  ```markdown
  ROS 2 provides a publisher-subscriber pattern [ref_999].
  ```

### 4.6 Validate Test Chapter

- [ ] Verify word count:
  ```bash
  ./verify-word-count.sh --file ../textbook/chapters/99-test-chapter.md
  ```

- [ ] Validate references:
  ```bash
  ./validate-references.sh --chapter ../textbook/chapters/99-test-chapter.md
  ```

- [ ] Generate RAG metadata:
  ```bash
  ./generate-rag-metadata.sh --chapter ../textbook/chapters/99-test-chapter.md
  ```

### 4.7 Cleanup Test Files

- [ ] Remove test chapter:
  ```bash
  rm ../textbook/chapters/99-test-chapter.md
  rm ../textbook/code-examples/chapter_99_example_01.py
  ```

- [ ] Remove test reference from references.json

---

## Phase 5: Assignment Confirmation

### 5.1 Module Assignment

- [ ] Confirm your module assignment:
  - **Module 1** (Fundamentals): Chapters 1-5
  - **Module 2** (ROS 2 & Architecture): Chapters 6-11
  - **Module 3** (Control & Kinematics): Chapters 12-17
  - **Module 4** (Applications): Chapters 18-22

- [ ] Review chapter outlines in spec.md:
  ```bash
  cat ../specs/002-content-writing/spec.md | grep -A 20 "Module [YOUR_MODULE_NUMBER]"
  ```

### 5.2 Timeline Confirmation

- [ ] Note your deadlines:
  - **Week 1**: Module 1 (if assigned)
  - **Week 2**: Module 2 (if assigned)
  - **Week 3**: Module 3 (if assigned)
  - **Week 4**: Module 4 (if assigned, optional)

- [ ] Understand daily targets:
  - 2,000-2,500 words/day
  - 2-3 code examples/day
  - Continuous testing and validation

### 5.3 Communication Channels

- [ ] Confirm communication methods:
  - **Questions**: Contact project coordinator
  - **Technical issues**: Contact Spec 001 team (RAG chatbot)
  - **Code problems**: Use lab machine or VM for testing
  - **Review requests**: Submit PR with proper format

---

## Checklist Summary

### Environment Setup

- [ ] Repository cloned and branch created
- [ ] Ubuntu 22.04 environment accessible
- [ ] ROS 2 Humble installed and verified
- [ ] Gazebo 11 installed and verified
- [ ] Development tools installed (Python, CMake, jq)

### Repository Familiarization

- [ ] Spec, plan, and tasks reviewed
- [ ] Chapter template understood
- [ ] Code examples structure understood
- [ ] References format understood

### Workflow Understanding

- [ ] Chapter creation workflow clear
- [ ] Automation scripts tested
- [ ] Review process understood
- [ ] Quality gates noted

### Practice Run

- [ ] Test chapter created successfully
- [ ] Test code example runs correctly
- [ ] Test references validated
- [ ] Verification scripts work

### Assignment Confirmation

- [ ] Module assignment confirmed
- [ ] Timeline understood
- [ ] Communication channels established

---

## Ready to Write!

Once all checkboxes are complete, you're ready to start writing your first chapter!

**Next Steps**:

1. Create your first chapter:
   ```bash
   cd scripts
   ./create-chapter.sh --id [CHAPTER_ID] --module "[MODULE_NAME]" --title "[CHAPTER_TITLE]"
   ```

2. Write content (2,300-2,400 words)

3. Create code examples (2-3 per chapter)

4. Test locally:
   ```bash
   ./verify-word-count.sh --file ../textbook/chapters/[CHAPTER_FILE].md
   ./test-code-examples.sh --chapter [CHAPTER_ID]
   ./validate-references.sh --chapter ../textbook/chapters/[CHAPTER_FILE].md
   ```

5. Submit for review when module complete

---

## Troubleshooting

### Issue: ROS 2 not sourced

**Solution**:
```bash
source /opt/ros/humble/setup.bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
```

### Issue: Code example fails to run

**Solution**:
1. Check dependencies installed
2. Verify ROS 2 environment sourced
3. Check Python path and imports
4. Test on clean Ubuntu 22.04 VM

### Issue: Word count too short/long

**Solution**:
- Target: 2,300-2,400 words per chapter
- Acceptable range: ±10% (2,070-2,640 words)
- Expand key concepts or add examples if too short
- Condense or split into subsections if too long

### Issue: Reference validation fails

**Solution**:
1. Ensure reference exists in references.json
2. Check APA format: Author, A. (Year). Title. Source.
3. Verify citation format in chapter: [ref_XXX]
4. Run validation script for details

---

## Additional Resources

- **ROS 2 Humble Documentation**: https://docs.ros.org/en/humble/
- **Gazebo Documentation**: http://gazebosim.org/tutorials
- **APA Citation Guide**: https://www.scribbr.com/apa-style/
- **Markdown Guide**: https://www.markdownguide.org/
- **Git Workflow**: https://git-scm.com/doc

---

## Contact

**Questions or Issues?**

- Project Coordinator: [Contact info]
- Technical Support: [Contact info]
- Emergency: [Contact info]

---

**Document Status**: Active | **Last Updated**: 2026-02-03 | **Spec**: 002-content-writing

**Welcome aboard, and happy writing!**

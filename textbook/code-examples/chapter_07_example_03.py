# URDF validation and analysis script
# Run with: python chapter_07_example_03.py <urdf_file>
# Expected output: Validation report with link/joint analysis and kinematic chain structure

import sys
import xml.etree.ElementTree as ET
import numpy as np


class URDFValidator:
    """Validates URDF files for common errors and computes kinematic properties."""

    def __init__(self, urdf_file):
        """Load and parse URDF file."""
        self.tree = ET.parse(urdf_file)
        self.root = self.tree.getroot()
        self.robot_name = self.root.get('name', 'unnamed')
        self.links = {}
        self.joints = {}
        self.errors = []
        self.warnings = []

    def validate(self):
        """Run all validation checks."""
        print(f"\n=== URDF Validation Report for '{self.robot_name}' ===\n")

        self._parse_links()
        self._parse_joints()
        self._check_kinematic_tree()
        self._validate_inertial_properties()
        self._validate_joint_limits()

        self._print_report()

    def _parse_links(self):
        """Extract and validate all links."""
        for link in self.root.findall('link'):
            name = link.get('name')
            if not name:
                self.errors.append("Link found without name attribute")
                continue

            self.links[name] = {
                'has_visual': link.find('visual') is not None,
                'has_collision': link.find('collision') is not None,
                'has_inertial': link.find('inertial') is not None,
                'element': link
            }

        print(f"Found {len(self.links)} links:")
        for name, props in self.links.items():
            visual_marker = "✓" if props['has_visual'] else "✗"
            collision_marker = "✓" if props['has_collision'] else "✗"
            inertial_marker = "✓" if props['has_inertial'] else "✗"
            print(f"  - {name:20s} [V:{visual_marker} C:{collision_marker} I:{inertial_marker}]")

            # Check for missing collision geometry
            if props['has_visual'] and not props['has_collision']:
                self.warnings.append(f"Link '{name}' has visual but no collision geometry")

    def _parse_joints(self):
        """Extract and validate all joints."""
        for joint in self.root.findall('joint'):
            name = joint.get('name')
            joint_type = joint.get('type', 'unknown')

            if not name:
                self.errors.append("Joint found without name attribute")
                continue

            parent_elem = joint.find('parent')
            child_elem = joint.find('child')

            if parent_elem is None or child_elem is None:
                self.errors.append(f"Joint '{name}' missing parent or child")
                continue

            parent = parent_elem.get('link')
            child = child_elem.get('link')

            self.joints[name] = {
                'type': joint_type,
                'parent': parent,
                'child': child,
                'axis': self._get_joint_axis(joint),
                'limits': self._get_joint_limits(joint),
                'element': joint
            }

        print(f"\nFound {len(self.joints)} joints:")
        for name, props in self.joints.items():
            print(f"  - {name:20s} [{props['type']:10s}] {props['parent']} -> {props['child']}")

    def _get_joint_axis(self, joint):
        """Extract joint axis vector."""
        axis_elem = joint.find('axis')
        if axis_elem is not None:
            xyz_str = axis_elem.get('xyz', '1 0 0')
            return [float(x) for x in xyz_str.split()]
        return [1, 0, 0]

    def _get_joint_limits(self, joint):
        """Extract joint limits."""
        limit_elem = joint.find('limit')
        if limit_elem is not None:
            return {
                'lower': float(limit_elem.get('lower', '0')),
                'upper': float(limit_elem.get('upper', '0')),
                'effort': float(limit_elem.get('effort', '0')),
                'velocity': float(limit_elem.get('velocity', '0'))
            }
        return None

    def _check_kinematic_tree(self):
        """Validate kinematic tree structure (no cycles, single root)."""
        print("\n=== Kinematic Tree Structure ===")

        # Find root links (links that are not children of any joint)
        child_links = {j['child'] for j in self.joints.values()}
        root_links = [name for name in self.links.keys() if name not in child_links]

        if len(root_links) == 0:
            self.errors.append("No root link found (cyclic kinematic tree)")
        elif len(root_links) > 1:
            self.warnings.append(f"Multiple root links found: {root_links}")
            print(f"Root links: {', '.join(root_links)}")
        else:
            print(f"Root link: {root_links[0]}")
            self._print_kinematic_tree(root_links[0], indent=0)

    def _print_kinematic_tree(self, link_name, indent=0):
        """Recursively print kinematic tree structure."""
        children = [(j_name, j['child'], j['type'])
                   for j_name, j in self.joints.items()
                   if j['parent'] == link_name]

        for joint_name, child_name, joint_type in children:
            print(f"  {'  ' * indent}└─ [{joint_type:10s}] {joint_name} -> {child_name}")
            self._print_kinematic_tree(child_name, indent + 1)

    def _validate_inertial_properties(self):
        """Check inertial properties for physics validity."""
        print("\n=== Inertial Properties Validation ===")

        for name, props in self.links.items():
            if not props['has_inertial']:
                continue

            inertial = props['element'].find('inertial')
            mass_elem = inertial.find('mass')
            inertia_elem = inertial.find('inertia')

            if mass_elem is None:
                self.errors.append(f"Link '{name}' has inertial but no mass")
                continue

            mass = float(mass_elem.get('value', '0'))
            if mass <= 0:
                self.errors.append(f"Link '{name}' has non-positive mass: {mass}")

            if inertia_elem is None:
                self.errors.append(f"Link '{name}' has inertial but no inertia tensor")
                continue

            # Extract inertia tensor
            ixx = float(inertia_elem.get('ixx', '0'))
            iyy = float(inertia_elem.get('iyy', '0'))
            izz = float(inertia_elem.get('izz', '0'))

            # Check for positive diagonal elements
            if ixx <= 0 or iyy <= 0 or izz <= 0:
                self.errors.append(f"Link '{name}' has non-positive inertia diagonal: [{ixx}, {iyy}, {izz}]")

            print(f"  {name:20s} mass={mass:6.3f} kg, I_diag=[{ixx:.6f}, {iyy:.6f}, {izz:.6f}]")

    def _validate_joint_limits(self):
        """Validate joint limits for revolute and prismatic joints."""
        print("\n=== Joint Limits Validation ===")

        for name, props in self.joints.items():
            if props['type'] not in ['revolute', 'prismatic']:
                continue

            limits = props['limits']
            if limits is None:
                self.errors.append(f"Joint '{name}' ({props['type']}) missing limit specification")
                continue

            if limits['lower'] >= limits['upper']:
                self.errors.append(f"Joint '{name}' has invalid limits: [{limits['lower']}, {limits['upper']}]")

            if limits['effort'] <= 0:
                self.warnings.append(f"Joint '{name}' has zero or negative effort limit")

            if limits['velocity'] <= 0:
                self.warnings.append(f"Joint '{name}' has zero or negative velocity limit")

            print(f"  {name:20s} pos:[{limits['lower']:6.2f}, {limits['upper']:6.2f}] "
                  f"eff:{limits['effort']:6.1f} vel:{limits['velocity']:6.2f}")

    def _print_report(self):
        """Print summary of validation results."""
        print("\n" + "=" * 60)
        print(f"Validation Summary: {len(self.errors)} errors, {len(self.warnings)} warnings")
        print("=" * 60)

        if self.errors:
            print("\nERRORS:")
            for error in self.errors:
                print(f"  ✗ {error}")

        if self.warnings:
            print("\nWARNINGS:")
            for warning in self.warnings:
                print(f"  ! {warning}")

        if not self.errors and not self.warnings:
            print("\n✓ URDF validation passed with no errors or warnings!")


def main():
    """Main function to run URDF validation."""
    if len(sys.argv) != 2:
        print("Usage: python chapter_07_example_03.py <urdf_file>")
        sys.exit(1)

    urdf_file = sys.argv[1]

    try:
        validator = URDFValidator(urdf_file)
        validator.validate()
    except FileNotFoundError:
        print(f"Error: URDF file '{urdf_file}' not found")
        sys.exit(1)
    except ET.ParseError as e:
        print(f"Error parsing URDF file: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

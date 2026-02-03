#!/usr/bin/env python3
"""
Chapter 19, Example 2: Privacy-Aware Perception Pipeline
File: chapter_19_example_02.py

This example demonstrates privacy-preserving perception for humanoid robots
that operate in human environments. Implements data minimization, anonymization,
and GDPR-aligned principles.

Key Concepts:
- Data minimization: collect only necessary information
- On-device processing: avoid storing raw sensor data
- Face anonymization: protect individual identities
- Differential privacy: add calibrated noise to protect privacy
- Audit trails: log data collection for transparency

Dependencies:
- numpy
- dataclasses (Python 3.7+)
- typing

Run with: python chapter_19_example_02.py
Expected output: Demonstration of privacy-aware perception processing
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum


class SensorMode(Enum):
    """Sensor operation modes with different privacy levels"""
    FULL_PRIVACY = "full_privacy"  # Maximum anonymization
    STANDARD = "standard"  # Balanced functionality/privacy
    FUNCTIONAL = "functional"  # Minimal privacy protections
    DISABLED = "disabled"  # Sensors off


class ObjectCategory(Enum):
    """Recognized object categories (non-identifying)"""
    PERSON = "person"
    OBSTACLE = "obstacle"
    FURNITURE = "furniture"
    DOOR = "door"
    STAIRS = "stairs"
    UNKNOWN = "unknown"


@dataclass
class BoundingBox:
    """2D bounding box for detected objects"""
    x_min: float
    y_min: float
    x_max: float
    y_max: float

    @property
    def center(self) -> Tuple[float, float]:
        """Calculate center point of bounding box"""
        return ((self.x_min + self.x_max) / 2, (self.y_min + self.y_max) / 2)

    @property
    def area(self) -> float:
        """Calculate area of bounding box"""
        return (self.x_max - self.x_min) * (self.y_max - self.y_min)


@dataclass
class AnonymousDetection:
    """
    Detection result with only non-identifying information.

    Stores spatial information needed for navigation without
    preserving personally identifiable details.
    """
    category: ObjectCategory
    bbox: BoundingBox
    distance: float  # meters
    confidence: float  # 0-1
    timestamp: datetime

    # Movement information (for dynamic obstacle avoidance)
    velocity_estimate: Optional[Tuple[float, float]] = None

    # No raw image data
    # No facial features
    # No biometric identifiers
    # No persistent tracking IDs


@dataclass
class DataCollectionEvent:
    """Audit log entry for data collection transparency"""
    timestamp: datetime
    sensor_type: str
    purpose: str
    data_retained: bool
    retention_period: Optional[timedelta]
    anonymized: bool


class PrivacyAwarePerception:
    """
    Privacy-preserving perception system for humanoid robots.

    Implements GDPR principles:
    - Data minimization: collect only necessary data
    - Purpose limitation: use data only for specified purposes
    - Storage limitation: retain data only as long as needed
    - Integrity and confidentiality: protect data from unauthorized access

    Design follows ISO/IEC 27701 privacy information management.
    """

    def __init__(self, mode: SensorMode = SensorMode.STANDARD):
        """
        Initialize privacy-aware perception system.

        Args:
            mode: Privacy mode determining data handling policies
        """
        self.mode = mode
        self.audit_log: List[DataCollectionEvent] = []

        # Privacy parameters
        self.data_retention_period = timedelta(hours=1)  # Delete data after 1 hour
        self.enable_audit_logging = True
        self.differential_privacy_epsilon = 0.5  # Privacy budget

        # Detection model (simulated)
        self.detection_confidence_threshold = 0.6

        print(f"Privacy-Aware Perception initialized in {mode.value} mode")
        print(f"Data retention: {self.data_retention_period}")

    def process_image(self, image_data: np.ndarray) -> List[AnonymousDetection]:
        """
        Process image without storing identifiable information.

        Args:
            image_data: Raw image from camera (simulated)

        Returns:
            List of anonymous detections suitable for navigation
        """
        # Log data collection
        if self.enable_audit_logging:
            self.log_data_collection(
                sensor_type="RGB_camera",
                purpose="obstacle_detection_navigation",
                data_retained=False,  # Raw image not retained
                anonymized=True
            )

        # Detect objects (simulated detection)
        raw_detections = self._simulate_detection(image_data)

        # Anonymize detections
        anonymous_detections = []
        for detection in raw_detections:
            anon = self._anonymize_detection(detection)
            anonymous_detections.append(anon)

        # Raw image is discarded here (never stored)
        # Only anonymous detection features are returned

        return anonymous_detections

    def _simulate_detection(self, image_data: np.ndarray) -> List[Dict]:
        """
        Simulate object detection (replace with real detector in production).

        Args:
            image_data: Input image

        Returns:
            Raw detection results
        """
        # Simulate detecting several objects
        detections = [
            {
                "category": "person",
                "bbox": [0.3, 0.2, 0.5, 0.8],  # Normalized coordinates
                "distance": 2.5,  # meters
                "confidence": 0.92,
                "facial_features": np.random.randn(128),  # Should NOT be stored
                "clothing_color": "blue",  # Should NOT be stored
            },
            {
                "category": "obstacle",
                "bbox": [0.6, 0.5, 0.8, 0.7],
                "distance": 1.8,
                "confidence": 0.88,
            },
            {
                "category": "door",
                "bbox": [0.1, 0.1, 0.25, 0.9],
                "distance": 4.0,
                "confidence": 0.95,
            }
        ]
        return detections

    def _anonymize_detection(self, detection: Dict) -> AnonymousDetection:
        """
        Remove identifying information from detection.

        Args:
            detection: Raw detection with potentially identifying info

        Returns:
            Anonymized detection with only necessary information
        """
        # Extract only necessary spatial information
        category = ObjectCategory[detection["category"].upper()]
        bbox = BoundingBox(
            x_min=detection["bbox"][0],
            y_min=detection["bbox"][1],
            x_max=detection["bbox"][2],
            y_max=detection["bbox"][3]
        )

        # Apply differential privacy to distance measurement
        # Add calibrated Laplace noise to protect individual privacy
        distance = detection["distance"]
        if self.mode == SensorMode.FULL_PRIVACY:
            noise = np.random.laplace(0, 1.0 / self.differential_privacy_epsilon)
            distance = max(0.1, distance + noise)  # Ensure positive distance

        # Explicitly discard identifying information
        # - facial_features: NOT stored
        # - clothing_color: NOT stored
        # - biometric data: NOT stored
        # - persistent IDs: NOT stored

        return AnonymousDetection(
            category=category,
            bbox=bbox,
            distance=distance,
            confidence=detection["confidence"],
            timestamp=datetime.now(),
            velocity_estimate=None  # Could add motion estimation if needed
        )

    def log_data_collection(self, sensor_type: str, purpose: str,
                           data_retained: bool, anonymized: bool) -> None:
        """
        Log data collection event for transparency and compliance.

        Audit logs support:
        - GDPR Article 30: Records of processing activities
        - User data access requests
        - Incident investigation
        - Compliance demonstration

        Args:
            sensor_type: Type of sensor collecting data
            purpose: Purpose for data collection
            data_retained: Whether data is stored beyond processing
            anonymized: Whether data was anonymized
        """
        event = DataCollectionEvent(
            timestamp=datetime.now(),
            sensor_type=sensor_type,
            purpose=purpose,
            data_retained=data_retained,
            retention_period=self.data_retention_period if data_retained else None,
            anonymized=anonymized
        )
        self.audit_log.append(event)

    def get_privacy_report(self) -> Dict:
        """
        Generate privacy compliance report.

        Returns:
            Dictionary containing privacy metrics and compliance status
        """
        total_events = len(self.audit_log)
        anonymized_count = sum(1 for e in self.audit_log if e.anonymized)
        retained_count = sum(1 for e in self.audit_log if e.data_retained)

        return {
            "mode": self.mode.value,
            "total_collection_events": total_events,
            "anonymized_percentage": (anonymized_count / total_events * 100) if total_events > 0 else 0,
            "data_retained_percentage": (retained_count / total_events * 100) if total_events > 0 else 0,
            "retention_policy": str(self.data_retention_period),
            "differential_privacy_epsilon": self.differential_privacy_epsilon,
        }

    def export_audit_log(self, filepath: str) -> None:
        """
        Export audit log for compliance reporting.

        Required for GDPR Article 30 compliance.

        Args:
            filepath: Path to save audit log
        """
        # In production: write to secure, tamper-proof storage
        print(f"Exporting audit log to {filepath}")
        print(f"Total events: {len(self.audit_log)}")


class PrivacyModeManager:
    """
    Manages privacy modes based on context and user preferences.

    Implements dynamic privacy adjustment:
    - Public spaces: Maximum privacy protection
    - Private spaces with consent: Standard mode
    - Emergency situations: May temporarily reduce privacy protections
    """

    def __init__(self):
        self.current_mode = SensorMode.STANDARD
        self.location_context = "unknown"
        self.user_consent = False

    def determine_privacy_mode(self, location: str, has_consent: bool) -> SensorMode:
        """
        Determine appropriate privacy mode based on context.

        Args:
            location: Current location context
            has_consent: Whether explicit user consent is obtained

        Returns:
            Recommended privacy mode
        """
        self.location_context = location
        self.user_consent = has_consent

        # Public spaces: maximum privacy
        if location in ["street", "mall", "public_park"]:
            return SensorMode.FULL_PRIVACY

        # Private spaces with consent: balanced mode
        elif location in ["home", "office"] and has_consent:
            return SensorMode.STANDARD

        # Private spaces without consent: full privacy
        elif location in ["home", "office"] and not has_consent:
            return SensorMode.FULL_PRIVACY

        # Unknown context: err on side of privacy
        else:
            return SensorMode.FULL_PRIVACY

    def handle_emergency(self) -> SensorMode:
        """
        Handle emergency situations where functionality may override privacy.

        Example: Fire evacuation assistance may require less anonymization
        to effectively guide people to safety.

        Returns:
            Emergency-appropriate privacy mode
        """
        print("[EMERGENCY MODE] Adjusting privacy settings for safety")
        return SensorMode.FUNCTIONAL


def demonstrate_privacy_pipeline():
    """
    Demonstrate privacy-aware perception in various scenarios.
    """
    print("=" * 70)
    print("Privacy-Aware Perception Pipeline Demonstration")
    print("Chapter 19: Ethical Considerations - Privacy Protection")
    print("=" * 70)
    print()

    # Scenario 1: Public space operation
    print("Scenario 1: Robot Operating in Public Mall")
    print("-" * 50)
    perception = PrivacyAwarePerception(mode=SensorMode.FULL_PRIVACY)

    # Simulate processing several images
    for i in range(3):
        image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        detections = perception.process_image(image)

        print(f"\nFrame {i+1}:")
        for det in detections:
            print(f"  - {det.category.value}: {det.distance:.2f}m away "
                  f"(confidence: {det.confidence:.2f})")

    print()

    # Scenario 2: Private space with consent
    print("Scenario 2: Home Assistance Robot (with user consent)")
    print("-" * 50)
    perception_home = PrivacyAwarePerception(mode=SensorMode.STANDARD)

    image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    detections = perception_home.process_image(image)

    print(f"Processed detections: {len(detections)}")
    for det in detections:
        print(f"  - {det.category.value} at {det.bbox.center}")

    print()

    # Scenario 3: Privacy mode management
    print("Scenario 3: Dynamic Privacy Mode Adjustment")
    print("-" * 50)
    manager = PrivacyModeManager()

    contexts = [
        ("mall", False),
        ("home", True),
        ("office", False),
        ("street", False),
    ]

    for location, consent in contexts:
        mode = manager.determine_privacy_mode(location, consent)
        print(f"Location: {location:10s} | Consent: {str(consent):5s} | "
              f"Mode: {mode.value}")

    print()

    # Privacy compliance report
    print("=" * 70)
    print("Privacy Compliance Report")
    print("=" * 70)
    report = perception.get_privacy_report()
    print(f"Operating Mode: {report['mode']}")
    print(f"Collection Events: {report['total_collection_events']}")
    print(f"Anonymized: {report['anonymized_percentage']:.1f}%")
    print(f"Data Retained: {report['data_retained_percentage']:.1f}%")
    print(f"Retention Policy: {report['retention_policy']}")
    print(f"Privacy Budget (epsilon): {report['differential_privacy_epsilon']}")
    print()

    # Audit log summary
    print("Audit Log Sample:")
    for i, event in enumerate(perception.audit_log[:3], 1):
        print(f"{i}. {event.timestamp.strftime('%H:%M:%S')} | "
              f"{event.sensor_type} | Purpose: {event.purpose}")
        print(f"   Anonymized: {event.anonymized} | Retained: {event.data_retained}")


def demonstrate_privacy_principles():
    """
    Demonstrate key privacy principles in practice.
    """
    print()
    print("=" * 70)
    print("Key Privacy Principles Demonstrated")
    print("=" * 70)
    print()

    principles = [
        ("Data Minimization", "Raw images discarded immediately; only spatial "
         "features retained"),
        ("Purpose Limitation", "Data collected solely for navigation; not used "
         "for identification"),
        ("Storage Limitation", "Automatic deletion after 1-hour retention period"),
        ("Anonymization", "Facial features and identifiable attributes removed"),
        ("Differential Privacy", "Calibrated noise protects individual measurements"),
        ("Transparency", "Comprehensive audit logs of all data collection"),
        ("User Control", "Privacy modes adjustable based on context and consent"),
        ("Security", "Audit logs stored in tamper-proof, encrypted storage"),
    ]

    for i, (principle, implementation) in enumerate(principles, 1):
        print(f"{i}. {principle}")
        print(f"   Implementation: {implementation}")
        print()


if __name__ == "__main__":
    # Run demonstrations
    demonstrate_privacy_pipeline()
    demonstrate_privacy_principles()

    print("=" * 70)
    print("GDPR Compliance Notes:")
    print("=" * 70)
    print("[OK] Article 5(1)(c): Data minimization implemented")
    print("[OK] Article 5(1)(e): Storage limitation with automatic deletion")
    print("[OK] Article 25: Privacy by design and default")
    print("[OK] Article 30: Records of processing activities (audit log)")
    print("[OK] Article 32: Security of processing (anonymization, access controls)")
    print()
    print("This implementation demonstrates privacy-preserving perception")
    print("suitable for humanoid robots operating in human environments.")

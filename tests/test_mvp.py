import unittest

from architect_ai.architecture_generator import generate_architecture
from architect_ai.explanation_layer import build_explanations
from architect_ai.requirements_parser import parse_requirements


class ArchitectAIMVPTests(unittest.TestCase):
    def test_parser_detects_scale_and_cloud(self) -> None:
        profile = parse_requirements("Build scalable AI chatbot backend on AWS with 1M users")
        self.assertEqual(profile.cloud, "aws")
        self.assertEqual(profile.estimated_users, 1_000_000)
        self.assertTrue(profile.high_scale)
        self.assertTrue(profile.ai_workload)

    def test_generator_builds_core_services(self) -> None:
        profile = parse_requirements("Build scalable ecommerce system with 500k users")
        spec = generate_architecture(profile)
        self.assertIn("VPC", spec.services)
        self.assertIn("Application Load Balancer", spec.services)
        self.assertIn("ECS Service", spec.services)
        self.assertIn("RDS", spec.services)
        self.assertIn("S3", spec.services)

    def test_explanations_cover_services(self) -> None:
        profile = parse_requirements("Build scalable AI chatbot backend with 1M users")
        spec = generate_architecture(profile)
        explanations = build_explanations(spec, profile)
        self.assertTrue(set(spec.services).issubset(set(explanations.keys())))


if __name__ == "__main__":
    unittest.main()


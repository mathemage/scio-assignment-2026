#!/usr/bin/env python3
"""
Requirements Verification Script

This script verifies as many requirements from the assignment as possible.
It performs automated checks on the codebase and provides a comprehensive report.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class RequirementVerifier:
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.results = []
        
    def print_header(self, text: str):
        """Print a formatted header"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")
        
    def print_requirement(self, name: str, status: str, percentage: int, details: str = ""):
        """Print a requirement check result"""
        if percentage == 100:
            icon = "✅"
            color = Colors.GREEN
            status_text = "PASS"
        elif percentage > 0:
            icon = "⚠️"
            color = Colors.YELLOW
            status_text = f"PARTIAL ({percentage}%)"
        else:
            icon = "❌"
            color = Colors.RED
            status_text = "FAIL"
            
        print(f"{icon} {Colors.BOLD}{name}{Colors.END}")
        print(f"   Status: {color}{status_text}{Colors.END}")
        if details:
            print(f"   {details}")
        print()
        
        self.results.append({
            'name': name,
            'status': status_text,
            'percentage': percentage,
            'details': details
        })
    
    def file_exists(self, path: str) -> bool:
        """Check if a file exists"""
        return (self.repo_root / path).exists()
    
    def file_contains(self, path: str, search_terms: List[str]) -> bool:
        """Check if file contains all search terms"""
        file_path = self.repo_root / path
        if not file_path.exists():
            return False
        
        try:
            content = file_path.read_text()
            return all(term in content for term in search_terms)
        except Exception:
            return False
    
    def directory_exists(self, path: str) -> bool:
        """Check if a directory exists"""
        return (self.repo_root / path).is_dir()
    
    def count_files_with_pattern(self, directory: str, pattern: str) -> int:
        """Count files containing a pattern"""
        count = 0
        dir_path = self.repo_root / directory
        if not dir_path.exists():
            return 0
            
        for file_path in dir_path.rglob("*.py"):
            try:
                if pattern in file_path.read_text():
                    count += 1
            except Exception:
                pass
        return count
    
    def check_authentication(self):
        """Verify authentication and RBAC implementation"""
        checks = {
            'OAuth endpoint': self.file_contains('backend/routers/auth.py', ['google', 'oauth']),
            'JWT utils': self.file_exists('backend/auth_utils.py'),
            'Auth dependencies': self.file_exists('backend/dependencies.py'),
            'User model with role': self.file_contains('backend/database.py', ['role', 'User']),
            'Frontend auth hook': self.file_exists('frontend/src/hooks/useAuth.tsx'),
            'Login page': self.file_exists('frontend/src/pages/Login.tsx'),
        }
        
        passed = sum(checks.values())
        total = len(checks)
        percentage = int((passed / total) * 100)
        
        details = f"Checks passed: {passed}/{total}"
        for check, result in checks.items():
            details += f"\n     - {check}: {'✓' if result else '✗'}"
        
        self.print_requirement(
            "1. Authentication & RBAC",
            "Implemented" if percentage == 100 else "Partial",
            percentage,
            details
        )
    
    def check_group_management(self):
        """Verify group management implementation"""
        checks = {
            'Group router': self.file_exists('backend/routers/groups.py'),
            'Group model': self.file_contains('backend/database.py', ['Group', 'name', 'goal_description']),
            'Teacher dashboard': self.file_exists('frontend/src/pages/TeacherDashboard.tsx'),
            'Group view': self.file_exists('frontend/src/pages/TeacherGroupView.tsx'),
            'Create endpoint': self.file_contains('backend/routers/groups.py', ['@router.post', 'create_group']),
            'List endpoint': self.file_contains('backend/routers/groups.py', ['@router.get', 'response_model']),
        }
        
        passed = sum(checks.values())
        total = len(checks)
        percentage = int((passed / total) * 100)
        
        details = f"Checks passed: {passed}/{total}"
        for check, result in checks.items():
            details += f"\n     - {check}: {'✓' if result else '✗'}"
        
        self.print_requirement(
            "2. Group Management",
            "Implemented" if percentage == 100 else "Partial",
            percentage,
            details
        )
    
    def check_qr_code_joining(self):
        """Verify QR code and group joining"""
        checks = {
            'QR code library': self.file_contains('frontend/package.json', ['react-qr-code']),
            'Join endpoint': self.file_contains('backend/routers/groups.py', ['join']),
            'Device ID tracking': self.file_contains('backend/database.py', ['device_id', 'GroupMembership']),
            'Join page': self.file_exists('frontend/src/pages/JoinGroup.tsx'),
            'Device utils': self.file_exists('frontend/src/utils/device.ts'),
            'QR display': self.file_contains('frontend/src/pages/TeacherGroupView.tsx', ['QRCode']),
        }
        
        passed = sum(checks.values())
        total = len(checks)
        percentage = int((passed / total) * 100)
        
        details = f"Checks passed: {passed}/{total}"
        for check, result in checks.items():
            details += f"\n     - {check}: {'✓' if result else '✗'}"
        
        self.print_requirement(
            "3. QR Code & Group Joining",
            "Implemented" if percentage == 100 else "Partial",
            percentage,
            details
        )
    
    def check_chat_interface(self):
        """Verify chat interface implementation"""
        checks = {
            'WebSocket support': self.file_contains('backend/routers/chat.py', ['WebSocket', 'websocket']),
            'Message model': self.file_contains('backend/database.py', ['Message', 'content']),
            'Chat router': self.file_exists('backend/routers/chat.py'),
            'Student chat view': self.file_exists('frontend/src/pages/StudentGroupView.tsx'),
            'WebSocket client': self.file_contains('frontend/src/services/api.ts', ['WebSocket', 'createWebSocket']),
            'Goal display': self.file_contains('frontend/src/pages/StudentGroupView.tsx', ['goal_description', 'Goal']),
        }
        
        passed = sum(checks.values())
        total = len(checks)
        percentage = int((passed / total) * 100)
        
        details = f"Checks passed: {passed}/{total}"
        for check, result in checks.items():
            details += f"\n     - {check}: {'✓' if result else '✗'}"
        
        self.print_requirement(
            "4. Chat Interface",
            "Implemented" if percentage == 100 else "Partial",
            percentage,
            details
        )
    
    def check_progress_tracking(self):
        """Verify progress tracking implementation"""
        checks = {
            'Progress endpoint': self.file_contains('backend/routers/chat.py', ['progress']),
            'Progress display (student)': self.file_contains('frontend/src/pages/StudentGroupView.tsx', ['progress', 'Progress']),
            'Progress display (teacher)': self.file_contains('frontend/src/pages/TeacherGroupView.tsx', ['progress', 'Progress']),
            'Real-time updates': self.file_contains('frontend/src/pages/StudentGroupView.tsx', ['progress_update']),
            'Progress bar': self.file_contains('frontend/src/pages/StudentGroupView.tsx', ['progressBar', 'width']),
        }
        
        # Check for advanced features (not implemented)
        advanced_checks = {
            'Boolean goals': self.file_contains('backend/routers/chat.py', ['boolean', 'checkmark']),
            'AI/NLP analysis': self.file_contains('backend/routers/chat.py', ['nlp', 'ai', 'analysis']),
            'Content quality check': self.file_contains('backend/routers/chat.py', ['quality', 'content_analysis']),
        }
        
        passed = sum(checks.values())
        total = len(checks)
        advanced_passed = sum(advanced_checks.values())
        
        # Percentage based on basic + advanced features
        percentage = int((passed / (total + len(advanced_checks))) * 100)
        
        details = f"Basic checks passed: {passed}/{total}"
        for check, result in checks.items():
            details += f"\n     - {check}: {'✓' if result else '✗'}"
        details += f"\n   Advanced features: {advanced_passed}/{len(advanced_checks)}"
        for check, result in advanced_checks.items():
            details += f"\n     - {check}: {'✓' if result else '✗'}"
        
        self.print_requirement(
            "5. Progress Tracking",
            "Partial" if percentage < 100 else "Implemented",
            percentage,
            details
        )
    
    def check_guidance_warnings(self):
        """Verify guidance and warnings implementation"""
        checks = {
            'Inactivity detection': self.file_contains('backend/routers/chat.py', ['inactivity', 'inactive']),
            'Warning indicators': self.file_contains('frontend/src/pages/StudentGroupView.tsx', ['warning', 'indicator']),
            'Teacher alerts': self.file_contains('frontend/src/pages/TeacherGroupView.tsx', ['alert', 'needs_help']),
            'Guidance messages': self.file_contains('backend/routers/chat.py', ['guidance', 'guide']),
        }
        
        passed = sum(checks.values())
        total = len(checks)
        percentage = int((passed / total) * 100)
        
        details = f"Checks passed: {passed}/{total}"
        for check, result in checks.items():
            details += f"\n     - {check}: {'✓' if result else '✗'}"
        
        self.print_requirement(
            "6. Guidance & Warnings",
            "Implemented" if percentage == 100 else "Not Implemented",
            percentage,
            details
        )
    
    def check_message_highlighting(self):
        """Verify message highlighting implementation"""
        checks = {
            'Green border': self.file_contains('frontend/src/pages/StudentGroupView.tsx', ['green', 'border', 'highlight']),
            'Message classification': self.file_contains('backend/routers/chat.py', ['classify', 'relevant']),
            'Progress-contributing': self.file_contains('backend/routers/chat.py', ['contributes', 'progress']),
        }
        
        passed = sum(checks.values())
        total = len(checks)
        percentage = int((passed / total) * 100)
        
        details = f"Checks passed: {passed}/{total}"
        for check, result in checks.items():
            details += f"\n     - {check}: {'✓' if result else '✗'}"
        
        self.print_requirement(
            "7. Message Highlighting",
            "Implemented" if percentage == 100 else "Not Implemented",
            percentage,
            details
        )
    
    def check_teacher_dashboard(self):
        """Verify teacher dashboard features"""
        checks = {
            'Teacher view exists': self.file_exists('frontend/src/pages/TeacherGroupView.tsx'),
            'Student list': self.file_contains('frontend/src/pages/TeacherGroupView.tsx', ['student', 'progress']),
            'Real-time monitoring': self.file_contains('frontend/src/pages/TeacherGroupView.tsx', ['WebSocket', 'progress_update']),
            'Message count': self.file_contains('frontend/src/pages/TeacherGroupView.tsx', ['messages_count']),
            'Last activity': self.file_contains('frontend/src/pages/TeacherGroupView.tsx', ['last_message_time']),
        }
        
        # Advanced features
        advanced_checks = {
            'Help indicator': self.file_contains('frontend/src/pages/TeacherGroupView.tsx', ['needs_help', 'help_requested']),
            'Mark as resolved': self.file_contains('frontend/src/pages/TeacherGroupView.tsx', ['resolve', 'resolved']),
        }
        
        passed = sum(checks.values())
        total = len(checks)
        advanced_passed = sum(advanced_checks.values())
        
        percentage = int((passed / (total + len(advanced_checks))) * 100)
        
        details = f"Basic checks passed: {passed}/{total}"
        for check, result in checks.items():
            details += f"\n     - {check}: {'✓' if result else '✗'}"
        details += f"\n   Advanced features: {advanced_passed}/{len(advanced_checks)}"
        for check, result in advanced_checks.items():
            details += f"\n     - {check}: {'✓' if result else '✗'}"
        
        self.print_requirement(
            "8. Teacher Dashboard",
            "Partial" if percentage < 100 else "Implemented",
            percentage,
            details
        )
    
    def check_technology_stack(self):
        """Verify technology stack requirements"""
        checks = {
            'TypeScript': self.file_exists('frontend/package.json') and 
                         self.file_contains('frontend/package.json', ['typescript']),
            'React frontend': self.file_contains('frontend/package.json', ['react']),
            'Backend API': self.file_exists('backend/main.py'),
            'Database': self.file_exists('backend/database.py'),
        }
        
        # Check what's different from requirements
        different = {
            'Blazor Server': self.file_contains('backend/main.py', ['Blazor', 'blazor', '.NET', 'dotnet']),
            'SQL Server': self.file_contains('backend/database.py', ['sqlserver', 'mssql', 'SQL Server']),
            'Tailwind CSS': self.file_contains('frontend/package.json', ['tailwind']),
            'Sass': self.file_contains('frontend/package.json', ['sass']),
        }
        
        passed = sum(checks.values())
        different_passed = sum(different.values())
        
        # Stack requirements partially met if core tech exists but different from spec
        percentage = 40  # Hardcoded based on analysis (TypeScript yes, but FastAPI not .NET)
        
        details = f"Core tech present: {passed}/{len(checks)}"
        for check, result in checks.items():
            details += f"\n     - {check}: {'✓' if result else '✗'}"
        details += f"\n   Required tech stack: {different_passed}/{len(different)}"
        for check, result in different.items():
            details += f"\n     - {check}: {'✓' if result else '✗'}"
        details += "\n   Note: Using FastAPI+React instead of Blazor+.NET"
        
        self.print_requirement(
            "9. Technology Stack",
            "Different stack used",
            percentage,
            details
        )
    
    def check_bonus_features(self):
        """Verify bonus features"""
        
        # Detail view
        detail_view = {
            'Expandable view': self.file_contains('frontend/src/pages/TeacherGroupView.tsx', ['expand', 'detail']),
            'Message filtering': self.file_contains('frontend/src/pages/TeacherGroupView.tsx', ['filter', 'student']),
        }
        detail_percentage = int((sum(detail_view.values()) / len(detail_view)) * 100)
        
        details_str = f"Checks: {sum(detail_view.values())}/{len(detail_view)}"
        for check, result in detail_view.items():
            details_str += f"\n     - {check}: {'✓' if result else '✗'}"
        
        self.print_requirement(
            "10. Detail View for Students (Bonus)",
            "Not Implemented" if detail_percentage == 0 else "Partial",
            detail_percentage,
            details_str
        )
        
        # Math rendering
        math_checks = {
            'KaTeX': self.file_contains('frontend/package.json', ['katex']),
            'MathJax': self.file_contains('frontend/package.json', ['mathjax']),
            'Math rendering': self.file_contains('frontend/src/pages/StudentGroupView.tsx', ['math', 'latex']),
        }
        math_percentage = int((sum(math_checks.values()) / len(math_checks)) * 100)
        
        math_details = f"Checks: {sum(math_checks.values())}/{len(math_checks)}"
        for check, result in math_checks.items():
            math_details += f"\n     - {check}: {'✓' if result else '✗'}"
        
        self.print_requirement(
            "11. Math & Code Rendering (Bonus)",
            "Not Implemented" if math_percentage == 0 else "Partial",
            math_percentage,
            math_details
        )
        
        # Voice input
        voice_checks = {
            'Speech API': self.file_contains('frontend/src/pages/StudentGroupView.tsx', ['Speech', 'recognition']),
            'Microphone button': self.file_contains('frontend/src/pages/StudentGroupView.tsx', ['microphone', 'voice']),
        }
        voice_percentage = int((sum(voice_checks.values()) / len(voice_checks)) * 100)
        
        voice_details = f"Checks: {sum(voice_checks.values())}/{len(voice_checks)}"
        for check, result in voice_checks.items():
            voice_details += f"\n     - {check}: {'✓' if result else '✗'}"
        
        self.print_requirement(
            "12. Voice Input (Bonus)",
            "Not Implemented" if voice_percentage == 0 else "Partial",
            voice_percentage,
            voice_details
        )
    
    def check_helper_scripts(self):
        """Verify helper scripts and tooling"""
        checks = {
            'Quick demo script': self.file_exists('scripts/quick_demo.sh'),
            'Role management': self.file_exists('scripts/make_teacher.sh'),
            'User listing': self.file_exists('scripts/list_users.py'),
            'Set role script': self.file_exists('scripts/set_user_role.py'),
            'Test data generator': self.file_exists('backend/create_test_data.py'),
            'Setup script': self.file_exists('setup.sh'),
        }
        
        passed = sum(checks.values())
        total = len(checks)
        percentage = int((passed / total) * 100)
        
        details = f"Checks passed: {passed}/{total}"
        for check, result in checks.items():
            details += f"\n     - {check}: {'✓' if result else '✗'}"
        
        self.print_requirement(
            "Helper Scripts & Tooling",
            "Excellent" if percentage == 100 else "Partial",
            percentage,
            details
        )
    
    def check_documentation(self):
        """Verify documentation quality"""
        checks = {
            'README.md': self.file_exists('README.md'),
            'FEATURES.md': self.file_exists('FEATURES.md'),
            'IMPLEMENTATION_SUMMARY.md': self.file_exists('IMPLEMENTATION_SUMMARY.md'),
            'Backend README': self.file_exists('backend/README.md'),
            'Frontend README': self.file_exists('frontend/README.md'),
            'Scripts README': self.file_exists('scripts/README.md'),
        }
        
        passed = sum(checks.values())
        total = len(checks)
        percentage = int((passed / total) * 100)
        
        details = f"Documentation files: {passed}/{total}"
        for check, result in checks.items():
            details += f"\n     - {check}: {'✓' if result else '✗'}"
        
        self.print_requirement(
            "Documentation Quality",
            "Excellent" if percentage >= 80 else "Good",
            percentage,
            details
        )
    
    def print_summary(self):
        """Print overall summary"""
        self.print_header("VERIFICATION SUMMARY")
        
        total_requirements = len(self.results)
        total_percentage = sum(r['percentage'] for r in self.results) / total_requirements if total_requirements > 0 else 0
        
        fully_met = len([r for r in self.results if r['percentage'] == 100])
        partial = len([r for r in self.results if 0 < r['percentage'] < 100])
        not_met = len([r for r in self.results if r['percentage'] == 0])
        
        print(f"Total Requirements Checked: {total_requirements}")
        print(f"  {Colors.GREEN}✅ Fully Met (100%): {fully_met}{Colors.END}")
        print(f"  {Colors.YELLOW}⚠️  Partially Met: {partial}{Colors.END}")
        print(f"  {Colors.RED}❌ Not Met (0%): {not_met}{Colors.END}")
        print(f"\n{Colors.BOLD}Overall Completion: {total_percentage:.1f}%{Colors.END}\n")
        
        # Core requirements only
        core_results = self.results[:9]  # First 9 are core requirements
        core_percentage = sum(r['percentage'] for r in core_results) / len(core_results) if core_results else 0
        print(f"{Colors.BOLD}Core Requirements Completion: {core_percentage:.1f}%{Colors.END}")
        
        # Bonus features
        bonus_results = self.results[9:12] if len(self.results) > 9 else []
        if bonus_results:
            bonus_percentage = sum(r['percentage'] for r in bonus_results) / len(bonus_results)
            print(f"{Colors.BOLD}Bonus Features Completion: {bonus_percentage:.1f}%{Colors.END}")
        
        print()
    
    def run_verification(self):
        """Run all verification checks"""
        self.print_header("REQUIREMENTS VERIFICATION REPORT")
        
        print("This script verifies the implementation against the assignment requirements.")
        print("Each requirement is checked automatically where possible.\n")
        
        self.print_header("CORE FUNCTIONALITY")
        
        self.check_authentication()
        self.check_group_management()
        self.check_qr_code_joining()
        self.check_chat_interface()
        self.check_progress_tracking()
        self.check_guidance_warnings()
        self.check_message_highlighting()
        self.check_teacher_dashboard()
        
        self.print_header("TECHNOLOGY STACK")
        self.check_technology_stack()
        
        self.print_header("BONUS FEATURES")
        self.check_bonus_features()
        
        self.print_header("ADDITIONAL CHECKS")
        self.check_helper_scripts()
        self.check_documentation()
        
        self.print_summary()
        
        print(f"\n{Colors.BOLD}For detailed requirement tracking, see:{Colors.END}")
        print(f"  📄 REQUIREMENTS_TRACKING.md\n")
        
        return self.results

def main():
    """Main entry point"""
    verifier = RequirementVerifier()
    results = verifier.run_verification()
    
    # Save results to JSON
    output_file = Path(__file__).parent.parent / "verification_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"{Colors.BOLD}Results saved to: {output_file}{Colors.END}\n")

if __name__ == "__main__":
    main()

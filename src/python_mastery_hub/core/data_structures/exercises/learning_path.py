"""
Learning path and educational progression management for Data Structures exercises.

This module handles the pedagogical aspects of the exercise system, including
skill progression tracking, prerequisite validation, and adaptive learning paths.
"""

from typing import Dict, List, Any, Optional, Set
from enum import Enum
import time


class SkillLevel(Enum):
    """Skill proficiency levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class LearningObjective(Enum):
    """Core learning objectives for data structures."""
    POINTER_MANIPULATION = "pointer_manipulation"
    MEMORY_MANAGEMENT = "memory_management"
    RECURSIVE_THINKING = "recursive_thinking"
    ALGORITHM_DESIGN = "algorithm_design"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    SYSTEM_DESIGN = "system_design"
    CONCURRENCY = "concurrency"


class LearningPath:
    """Manages educational progression and learning paths."""
    
    # Define skill dependencies and progression
    SKILL_PREREQUISITES = {
        LearningObjective.MEMORY_MANAGEMENT: {LearningObjective.POINTER_MANIPULATION},
        LearningObjective.RECURSIVE_THINKING: {LearningObjective.ALGORITHM_DESIGN},
        LearningObjective.PERFORMANCE_ANALYSIS: {LearningObjective.ALGORITHM_DESIGN},
        LearningObjective.SYSTEM_DESIGN: {
            LearningObjective.PERFORMANCE_ANALYSIS,
            LearningObjective.MEMORY_MANAGEMENT
        },
        LearningObjective.CONCURRENCY: {LearningObjective.SYSTEM_DESIGN}
    }
    
    # Exercise skill mappings
    EXERCISE_SKILLS = {
        "linkedlist": {
            LearningObjective.POINTER_MANIPULATION,
            LearningObjective.MEMORY_MANAGEMENT,
            LearningObjective.ALGORITHM_DESIGN
        },
        "bst": {
            LearningObjective.RECURSIVE_THINKING,
            LearningObjective.ALGORITHM_DESIGN,
            LearningObjective.PERFORMANCE_ANALYSIS,
            LearningObjective.MEMORY_MANAGEMENT
        },
        "cache": {
            LearningObjective.SYSTEM_DESIGN,
            LearningObjective.PERFORMANCE_ANALYSIS,
            LearningObjective.CONCURRENCY,
            LearningObjective.MEMORY_MANAGEMENT
        }
    }
    
    @classmethod
    def get_recommended_sequence(cls) -> List[Dict[str, Any]]:
        """Get recommended exercise sequence with pedagogical rationale."""
        return [
            {
                "exercise": "linkedlist",
                "position": 1,
                "rationale": "Foundation for pointer-based data structures",
                "key_concepts": ["Pointers", "Memory layout", "Basic algorithms"],
                "difficulty_progression": "Introduces core concepts gradually",
                "estimated_hours": (1, 2),
                "prerequisites": [],
                "unlocks": ["Tree structures", "Advanced pointer manipulation"]
            },
            {
                "exercise": "bst",
                "position": 2,
                "rationale": "Builds recursive thinking on pointer foundation",
                "key_concepts": ["Recursion", "Tree traversal", "Search algorithms"],
                "difficulty_progression": "Adds algorithmic complexity to pointer skills",
                "estimated_hours": (2, 3),
                "prerequisites": ["linkedlist"],
                "unlocks": ["Advanced tree algorithms", "Graph structures"]
            },
            {
                "exercise": "cache",
                "position": 3,
                "rationale": "Integrates all skills in system design context",
                "key_concepts": ["System design", "Performance optimization", "Concurrency"],
                "difficulty_progression": "Applies learned concepts to real-world problems",
                "estimated_hours": (2, 3),
                "prerequisites": ["linkedlist", "bst"],
                "unlocks": ["Distributed systems", "Advanced caching strategies"]
            }
        ]
    
    @classmethod
    def validate_prerequisites(cls, exercise_name: str, completed_exercises: Set[str]) -> Dict[str, Any]:
        """Validate if prerequisites are met for an exercise."""
        sequence = cls.get_recommended_sequence()
        exercise_info = next((ex for ex in sequence if ex["exercise"] == exercise_name), None)
        
        if not exercise_info:
            return {"valid": False, "error": f"Unknown exercise: {exercise_name}"}
        
        required_prereqs = set(exercise_info["prerequisites"])
        missing_prereqs = required_prereqs - completed_exercises
        
        return {
            "valid": len(missing_prereqs) == 0,
            "missing_prerequisites": list(missing_prereqs),
            "recommendations": cls._get_prerequisite_recommendations(missing_prereqs)
        }
    
    @classmethod
    def _get_prerequisite_recommendations(cls, missing_prereqs: Set[str]) -> List[str]:
        """Get specific recommendations for missing prerequisites."""
        recommendations = []
        for prereq in missing_prereqs:
            if prereq == "linkedlist":
                recommendations.append("Complete LinkedList exercise to understand pointer manipulation")
            elif prereq == "bst":
                recommendations.append("Complete BST exercise to master recursive algorithms")
        return recommendations
    
    @classmethod
    def get_skill_progression_map(cls) -> Dict[str, Any]:
        """Get detailed skill progression mapping across exercises."""
        skill_levels = {}
        
        for exercise, skills in cls.EXERCISE_SKILLS.items():
            for skill in skills:
                if skill not in skill_levels:
                    skill_levels[skill] = {
                        "exercises": [],
                        "progression": []
                    }
                
                skill_levels[skill]["exercises"].append(exercise)
        
        # Define progression levels for each skill
        progressions = {
            LearningObjective.POINTER_MANIPULATION: [
                {"level": "Basic", "exercise": "linkedlist", "concepts": ["Node creation", "Link manipulation"]},
                {"level": "Intermediate", "exercise": "bst", "concepts": ["Tree node pointers", "Parent-child relationships"]},
                {"level": "Advanced", "exercise": "cache", "concepts": ["Complex pointer patterns", "Memory optimization"]}
            ],
            LearningObjective.ALGORITHM_DESIGN: [
                {"level": "Basic", "exercise": "linkedlist", "concepts": ["Linear algorithms", "Iteration patterns"]},
                {"level": "Intermediate", "exercise": "bst", "concepts": ["Recursive algorithms", "Divide and conquer"]},
                {"level": "Advanced", "exercise": "cache", "concepts": ["Hybrid algorithms", "Performance-driven design"]}
            ],
            LearningObjective.PERFORMANCE_ANALYSIS: [
                {"level": "Introduction", "exercise": "bst", "concepts": ["Big O notation", "Time complexity"]},
                {"level": "Application", "exercise": "cache", "concepts": ["Space-time tradeoffs", "Real-world optimization"]}
            ]
        }
        
        for skill, progression in progressions.items():
            if skill in skill_levels:
                skill_levels[skill]["progression"] = progression
        
        return skill_levels
    
    @classmethod
    def generate_personalized_path(cls, 
                                 current_skills: Set[LearningObjective],
                                 target_skills: Set[LearningObjective],
                                 time_constraint_hours: Optional[int] = None) -> Dict[str, Any]:
        """Generate personalized learning path based on current and target skills."""
        
        # Calculate skill gaps
        skill_gaps = target_skills - current_skills
        
        # Find exercises that address skill gaps
        relevant_exercises = []
        for exercise, exercise_skills in cls.EXERCISE_SKILLS.items():
            overlap = exercise_skills & skill_gaps
            if overlap:
                relevant_exercises.append({
                    "exercise": exercise,
                    "skills_addressed": list(overlap),
                    "skill_coverage": len(overlap) / len(skill_gaps) if skill_gaps else 0
                })
        
        # Sort by skill coverage
        relevant_exercises.sort(key=lambda x: x["skill_coverage"], reverse=True)
        
        # Apply time constraints if specified
        path = []
        total_time = 0
        covered_skills = set()
        
        for exercise_info in relevant_exercises:
            sequence_info = next(
                ex for ex in cls.get_recommended_sequence() 
                if ex["exercise"] == exercise_info["exercise"]
            )
            
            exercise_time = sequence_info["estimated_hours"][1]  # Use max estimate
            
            if time_constraint_hours and (total_time + exercise_time > time_constraint_hours):
                continue
            
            path.append({
                **exercise_info,
                **sequence_info,
                "cumulative_time": total_time + exercise_time
            })
            
            total_time += exercise_time
            covered_skills.update(exercise_info["skills_addressed"])
            
            # Stop if we've covered all target skills
            if covered_skills >= skill_gaps:
                break
        
        return {
            "personalized_path": path,
            "total_estimated_hours": total_time,
            "skills_covered": list(covered_skills),
            "remaining_skill_gaps": list(skill_gaps - covered_skills),
            "coverage_percentage": len(covered_skills) / len(skill_gaps) * 100 if skill_gaps else 100
        }
    
    @classmethod
    def assess_exercise_difficulty(cls, exercise_name: str, student_background: Dict[str, Any]) -> Dict[str, Any]:
        """Assess exercise difficulty for a specific student background."""
        
        # Default difficulty levels
        base_difficulties = {
            "linkedlist": 3,  # 1-5 scale
            "bst": 4,
            "cache": 5
        }
        
        base_difficulty = base_difficulties.get(exercise_name, 3)
        
        # Adjust based on student background
        programming_years = student_background.get("programming_years", 0)
        has_cs_degree = student_background.get("has_cs_degree", False)
        familiar_concepts = set(student_background.get("familiar_concepts", []))
        
        # Exercise-specific concept requirements
        concept_requirements = {
            "linkedlist": {"pointers", "oop", "basic_algorithms"},
            "bst": {"recursion", "trees", "pointers", "algorithms"},
            "cache": {"threading", "system_design", "performance_optimization", "data_structures"}
        }
        
        required_concepts = concept_requirements.get(exercise_name, set())
        concept_coverage = len(familiar_concepts & required_concepts) / len(required_concepts) if required_concepts else 1
        
        # Calculate adjusted difficulty
        experience_modifier = min(programming_years * 0.2, 1.0)  # Cap at 1.0
        education_modifier = 0.5 if has_cs_degree else 0
        concept_modifier = concept_coverage
        
        adjusted_difficulty = base_difficulty * (1 - experience_modifier - education_modifier - concept_modifier * 0.3)
        adjusted_difficulty = max(1, min(5, adjusted_difficulty))  # Keep in 1-5 range
        
        # Generate recommendations
        recommendations = []
        if concept_coverage < 0.7:
            missing_concepts = required_concepts - familiar_concepts
            recommendations.append(f"Review these concepts first: {', '.join(missing_concepts)}")
        
        if adjusted_difficulty >= 4:
            recommendations.append("Consider additional preparation or study time")
            recommendations.append("Break the exercise into smaller chunks")
        
        return {
            "base_difficulty": base_difficulty,
            "adjusted_difficulty": round(adjusted_difficulty, 1),
            "difficulty_factors": {
                "programming_experience": experience_modifier,
                "educational_background": education_modifier,
                "concept_familiarity": concept_modifier
            },
            "concept_coverage": round(concept_coverage * 100, 1),
            "missing_concepts": list(required_concepts - familiar_concepts),
            "recommendations": recommendations,
            "estimated_completion_time_hours": cls._estimate_completion_time(exercise_name, adjusted_difficulty)
        }
    
    @classmethod
    def _estimate_completion_time(cls, exercise_name: str, difficulty: float) -> tuple:
        """Estimate completion time based on difficulty adjustment."""
        base_times = {
            "linkedlist": (1, 2),
            "bst": (2, 3),
            "cache": (2, 3)
        }
        
        base_min, base_max = base_times.get(exercise_name, (1, 2))
        
        # Adjust based on difficulty
        multiplier = difficulty / 3.0  # 3 is average difficulty
        
        adjusted_min = round(base_min * multiplier, 1)
        adjusted_max = round(base_max * multiplier, 1)
        
        return (adjusted_min, adjusted_max)
    
    @classmethod
    def track_progress(cls, student_id: str, exercise_name: str, completion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track student progress through exercises (placeholder for full implementation)."""
        
        # This would integrate with a database in a real system
        progress_entry = {
            "student_id": student_id,
            "exercise": exercise_name,
            "completion_time": completion_data.get("completion_time_hours"),
            "attempts": completion_data.get("attempts", 1),
            "success_rate": completion_data.get("success_rate", 1.0),
            "timestamp": time.time(),
            "skills_demonstrated": list(cls.EXERCISE_SKILLS.get(exercise_name, set()))
        }
        
        # Calculate performance metrics
        sequence = cls.get_recommended_sequence()
        exercise_info = next((ex for ex in sequence if ex["exercise"] == exercise_name), None)
        
        if exercise_info:
            expected_time = exercise_info["estimated_hours"][1]
            actual_time = completion_data.get("completion_time_hours", expected_time)
            performance_ratio = expected_time / actual_time if actual_time > 0 else 1.0
            
            progress_entry.update({
                "performance_vs_expected": performance_ratio,
                "performance_category": cls._categorize_performance(performance_ratio)
            })
        
        return progress_entry
    
    @classmethod
    def _categorize_performance(cls, performance_ratio: float) -> str:
        """Categorize student performance."""
        if performance_ratio >= 1.5:
            return "excellent"
        elif performance_ratio >= 1.2:
            return "above_average"
        elif performance_ratio >= 0.8:
            return "average"
        elif performance_ratio >= 0.6:
            return "below_average"
        else:
            return "needs_improvement"
    
    @classmethod
    def get_next_recommendations(cls, completed_exercises: Set[str], 
                               student_performance: Dict[str, float]) -> List[Dict[str, Any]]:
        """Get next exercise recommendations based on completion history."""
        
        sequence = cls.get_recommended_sequence()
        available_exercises = []
        
        for exercise_info in sequence:
            exercise_name = exercise_info["exercise"]
            
            # Skip if already completed
            if exercise_name in completed_exercises:
                continue
            
            # Check prerequisites
            prereq_validation = cls.validate_prerequisites(exercise_name, completed_exercises)
            if not prereq_validation["valid"]:
                continue
            
            # Calculate recommendation score
            performance_avg = sum(student_performance.values()) / len(student_performance) if student_performance else 0.5
            
            # Recommend easier exercises for struggling students
            base_difficulty = {"linkedlist": 3, "bst": 4, "cache": 5}.get(exercise_name, 3)
            difficulty_match = 1.0 - abs(base_difficulty - (performance_avg * 5)) / 5
            
            recommendation_score = difficulty_match * 100
            
            available_exercises.append({
                **exercise_info,
                "recommendation_score": recommendation_score,
                "rationale": cls._generate_recommendation_rationale(exercise_name, performance_avg)
            })
        
        # Sort by recommendation score
        available_exercises.sort(key=lambda x: x["recommendation_score"], reverse=True)
        
        return available_exercises[:3]  # Return top 3 recommendations
    
    @classmethod
    def _generate_recommendation_rationale(cls, exercise_name: str, performance_avg: float) -> str:
        """Generate rationale for exercise recommendation."""
        if performance_avg > 0.8:
            return f"Given your strong performance, {exercise_name} will provide an appropriate challenge"
        elif performance_avg > 0.6:
            return f"{exercise_name} builds naturally on your current skills"
        else:
            return f"{exercise_name} provides good practice to strengthen fundamentals"


# Convenience functions for common operations
def get_recommended_sequence():
    """Get the recommended exercise sequence."""
    return LearningPath.get_recommended_sequence()

def validate_prerequisites(exercise_name: str, completed_exercises: Set[str]):
    """Validate prerequisites for an exercise."""
    return LearningPath.validate_prerequisites(exercise_name, completed_exercises)

def assess_difficulty(exercise_name: str, student_background: Dict[str, Any]):
    """Assess exercise difficulty for a student."""
    return LearningPath.assess_exercise_difficulty(exercise_name, student_background)

def generate_personalized_path(current_skills: Set[LearningObjective], 
                             target_skills: Set[LearningObjective],
                             time_constraint_hours: Optional[int] = None):
    """Generate a personalized learning path."""
    return LearningPath.generate_personalized_path(current_skills, target_skills, time_constraint_hours)
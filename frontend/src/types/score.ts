export type Grade = "A" | "B" | "C" | "D" | "F";

export interface GradeInfo {
  grade: Grade;
  label: string;
  color: string;
  bgColor: string;
  min: number;
  max: number;
}

export const GRADE_CONFIG: Record<Grade, GradeInfo> = {
  A: {
    grade: "A",
    label: "Minimal concern",
    color: "text-green-700",
    bgColor: "bg-green-100",
    min: 0,
    max: 20,
  },
  B: {
    grade: "B",
    label: "Low concern",
    color: "text-lime-700",
    bgColor: "bg-lime-100",
    min: 20,
    max: 40,
  },
  C: {
    grade: "C",
    label: "Moderate concern",
    color: "text-yellow-700",
    bgColor: "bg-yellow-100",
    min: 40,
    max: 60,
  },
  D: {
    grade: "D",
    label: "High concern",
    color: "text-orange-700",
    bgColor: "bg-orange-100",
    min: 60,
    max: 80,
  },
  F: {
    grade: "F",
    label: "Very high concern",
    color: "text-red-700",
    bgColor: "bg-red-100",
    min: 80,
    max: 100,
  },
};

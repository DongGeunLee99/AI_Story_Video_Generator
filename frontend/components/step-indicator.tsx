import { Check } from "lucide-react"
import { cn } from "@/lib/utils"

type StepIndicatorProps = {
  currentStep: number
}

const steps = [
  { number: 1, label: "원고 입력" },
  { number: 2, label: "TTS 선택" },
  { number: 3, label: "BGM 선택" },
  { number: 4, label: "영상 설정" },
  { number: 5, label: "영상 생성" },
  { number: 6, label: "완료" },
]

export function StepIndicator({ currentStep }: StepIndicatorProps) {
  return (
    <div className="sticky top-8 space-y-2">
      {steps.map((step, index) => {
        const isCompleted = currentStep > step.number
        const isCurrent = currentStep === step.number
        const isUpcoming = currentStep < step.number

        return (
          <div key={step.number} className="flex items-start gap-3">
            {/* Connector line */}
            {index < steps.length - 1 && <div className="absolute left-[15px] top-8 h-8 w-0.5 bg-border" />}

            {/* Step circle */}
            <div
              className={cn(
                "relative z-10 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full border-2 transition-colors",
                isCompleted && "border-primary bg-primary text-primary-foreground",
                isCurrent && "border-primary bg-background text-primary",
                isUpcoming && "border-border bg-background text-muted-foreground",
              )}
            >
              {isCompleted ? (
                <Check className="h-4 w-4" />
              ) : (
                <span className="text-sm font-semibold">{step.number}</span>
              )}
            </div>

            {/* Step label */}
            <div className="flex-1 pt-1">
              <p
                className={cn(
                  "text-sm font-medium transition-colors",
                  isCurrent && "text-foreground",
                  (isCompleted || isUpcoming) && "text-muted-foreground",
                )}
              >
                {step.label}
              </p>
            </div>
          </div>
        )
      })}
    </div>
  )
}

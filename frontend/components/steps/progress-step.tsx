"use client"

import { useEffect, useRef, useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import type { VideoGeneratorData } from "@/app/page"
import { FileText, ImageIcon, Music2, Video, CheckCircle2 } from "lucide-react"
import { Progress } from "@/components/ui/progress"
import { cn } from "@/lib/utils"
import { createVideoWithResponse } from "@/lib/api"

type ProgressStepProps = {
  data: VideoGeneratorData
  updateData: (data: Partial<VideoGeneratorData>) => void
  onNext: () => void
}

const steps = [
  { id: 1, label: "원고 처리 중...", icon: FileText },
  { id: 2, label: "이미지 생성 중...", icon: ImageIcon },
  { id: 3, label: "오디오 생성 중...", icon: Music2 },
  { id: 4, label: "영상 생성 중...", icon: Video },
  { id: 5, label: "완료!", icon: CheckCircle2 },
]

export function ProgressStep({ data, updateData, onNext }: ProgressStepProps) {
  const [currentStep, setCurrentStep] = useState(1)
  const [progress, setProgress] = useState(0)
  const hasTriggeredRef = useRef(false)

  // --------------------------------------
  // 1) Python 영상 생성 API — 단 한 번만 실행
  // --------------------------------------
  useEffect(() => {
    if (hasTriggeredRef.current) return // StrictMode 중복 실행 방지
    hasTriggeredRef.current = true

    async function generate() {
      try {
        console.log("[Progress] 영상 생성 API 호출 시작", data)

        const { videoUrl, meta } = await createVideoWithResponse(data)

        console.log("[Progress] 영상 생성 완료:", videoUrl)
        updateData({ videoUrl })

        setCurrentStep(5)
        setTimeout(() => onNext(), 800)

      } catch (err) {
        console.error("[Progress] 영상 생성 실패:", err)
        alert("영상 생성 중 오류가 발생했습니다.")
      }
    }

    generate()
  }, [data, updateData, onNext])  // mount 시 단 한 번 실행


  // --------------------------------------
  // 2) UI 단계(progress bar) 자연스럽게 증가
  // --------------------------------------
  useEffect(() => {
    if (currentStep >= 5) return

    const timer = setInterval(() => {
      setCurrentStep(prev => (prev < 4 ? prev + 1 : prev))
    }, 2500) // 각 스텝 2.5초 표시

    return () => clearInterval(timer)
  }, [currentStep])

  useEffect(() => {
    setProgress((currentStep / steps.length) * 100)
  }, [currentStep])

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold">영상을 생성하고 있습니다</h2>
        <p className="mt-2 text-muted-foreground">잠시만 기다려주세요. 곧 완성됩니다!</p>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="space-y-8">

            {/* 전체 진행률 */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium">전체 진행률</span>
                <span className="text-muted-foreground">
                  [{currentStep}/{steps.length}]
                </span>
              </div>
              <Progress value={progress} className="h-2" />
            </div>

            {/* 단계 UI */}
            <div className="space-y-4">
              {steps.map((step) => {
                const Icon = step.icon
                const isCompleted = currentStep > step.id
                const isCurrent = currentStep === step.id
                const isPending = currentStep < step.id

                return (
                  <div
                    key={step.id}
                    className={cn(
                      "flex items-center gap-4 rounded-lg border p-4 transition-all",
                      isCurrent && "border-primary bg-primary/5",
                      isCompleted && "border-primary/30 bg-muted/50",
                      isPending && "border-border bg-muted/20",
                    )}
                  >
                    <div
                      className={cn(
                        "flex h-10 w-10 items-center justify-center rounded-full",
                        isCurrent && "animate-pulse bg-primary text-primary-foreground",
                        isCompleted && "bg-primary text-primary-foreground",
                        isPending && "bg-muted text-muted-foreground",
                      )}
                    >
                      <Icon className="h-5 w-5" />
                    </div>

                    <div className="flex-1">
                      <p
                        className={cn(
                          "font-medium",
                          isCurrent && "text-foreground",
                          isCompleted && "text-foreground",
                          isPending && "text-muted-foreground",
                        )}
                      >
                        {step.label}
                      </p>
                    </div>

                    {isCompleted && <CheckCircle2 className="h-5 w-5 text-primary" />}
                  </div>
                )
              })}
            </div>

            {/* 로딩 UI */}
            {currentStep < 5 && (
              <div className="rounded-lg border bg-muted/30 p-8">
                <div className="flex flex-col items-center justify-center space-y-4">
                  <div className="relative h-20 w-20">
                    <div className="absolute inset-0 animate-spin rounded-full border-4 border-primary/20 border-t-primary" />
                  </div>
                  <p className="text-center text-sm text-muted-foreground">
                    고품질 영상을 생성하는 중입니다...
                  </p>
                </div>
              </div>
            )}

          </div>
        </CardContent>
      </Card>
    </div>
  )
}

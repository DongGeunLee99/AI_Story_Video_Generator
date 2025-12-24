"use client"

import { useState } from "react"
import { ManuscriptStep } from "@/components/steps/manuscript-step"
import { TTSStep } from "@/components/steps/tts-step"
import { BGMStep } from "@/components/steps/bgm-step"
import { SettingsStep } from "@/components/steps/settings-step"
import { ProgressStep } from "@/components/steps/progress-step"
import { CompletionStep } from "@/components/steps/completion-step"
import { StepIndicator } from "@/components/step-indicator"

export type VideoGeneratorData = {
  manuscript?: string
  manuscriptSource?: "text" | "youtube"
  youtubeUrl?: string
  wordCount?: number
  estimatedDuration?: string
  summary?: string
  chapters?: string[]
  ttsVoice?: string
  bgmGenre?: string
  bgmType?: string
  videoRatio?: string
  videoUrl?: string
}

export default function HomePage() {
  const [currentStep, setCurrentStep] = useState(1)
  const [data, setData] = useState<VideoGeneratorData>({})

  const updateData = (newData: Partial<VideoGeneratorData>) => {
    setData((prev) => ({ ...prev, ...newData }))
  }

  const nextStep = () => {
    setCurrentStep((prev) => Math.min(prev + 1, 6))
  }

  const prevStep = () => {
    setCurrentStep((prev) => Math.max(prev - 1, 1))
  }

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return <ManuscriptStep data={data} updateData={updateData} onNext={nextStep} />
      case 2:
        return <TTSStep data={data} updateData={updateData} onNext={nextStep} onBack={prevStep} />
      case 3:
        return <BGMStep data={data} updateData={updateData} onNext={nextStep} onBack={prevStep} />
      case 4:
        return <SettingsStep data={data} updateData={updateData} onNext={nextStep} onBack={prevStep} />
      case 5:
        return <ProgressStep data={data} updateData={updateData} onNext={nextStep} />
      case 6:
        return (
          <CompletionStep
            data={data}
            onRestart={() => {
              setCurrentStep(1)
              setData({})
            }}
          />
        )
      default:
        return null
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-foreground">스토리 영상 생성기</h1>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="flex gap-8">
          <aside className="w-64 flex-shrink-0">
            <StepIndicator currentStep={currentStep} />
          </aside>

          <main className="flex-1 max-w-4xl">{renderStep()}</main>
        </div>
      </div>
    </div>
  )
}

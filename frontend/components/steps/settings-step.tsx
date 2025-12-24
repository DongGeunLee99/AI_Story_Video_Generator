"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import type { VideoGeneratorData } from "@/app/page"
import { LucideRatio as AspectRatio, Settings } from "lucide-react"
import { cn } from "@/lib/utils"

type SettingsStepProps = {
  data: VideoGeneratorData
  updateData: (data: Partial<VideoGeneratorData>) => void
  onNext: () => void
  onBack: () => void
}

const videoRatios = [
  { id: "1536x1024", label: "1536 x 1024", description: "가로영상" },
  { id: "1024x1536", label: "1024 x 1536", description: "세로형 쇼츠" },
]

const voiceNameMap: Record<string, string> = {
  "ko-KR-Wavenet-d": "남성-A",
  "ko-KR-Wavenet-b": "남성-B",
  "ko-KR-Wavenet-a": "여성-A",
  "ko-KR-Wavenet-c": "여성-B",
}

const genreNameMap: Record<string, string> = {
  romance: "로맨스",
  noir: "느와르",
  horror: "공포",
  daily: "일상썰",
}

const typeNameMap: Record<string, string> = {
  A: "A타입",
  B: "B타입",
  C: "C타입",
}

export function SettingsStep({ data, updateData, onNext, onBack }: SettingsStepProps) {
  const [selectedRatio, setSelectedRatio] = useState(data.videoRatio || "1536x1024")

  // ⭐ 핵심: 영상 생성 버튼을 눌러도 Python 실행 안 함
  const handleNext = () => {
    console.log("[SettingsStep] 영상 생성 시작 버튼 클릭됨")

    // 선택된 값 반영
    updateData({
      videoRatio: selectedRatio,
    })

    // ProgressStep으로 이동 → 여기서 createVideoWithResponse 실행됨(딱 한 번)
    onNext()
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-balance">영상 설정을 확인해주세요</h2>
        <p className="mt-2 text-muted-foreground">최종 설정을 확인하고 영상을 생성합니다</p>
      </div>

      {/* 요약 카드(변경 없음) */}
      <Card>
        <CardHeader>
          <CardTitle>선택한 옵션 요약</CardTitle>
          <CardDescription>아래 설정으로 영상이 생성됩니다</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-lg border bg-muted/50 p-4">
              <p className="text-sm text-muted-foreground">원고</p>
              <p className="mt-1 font-medium">{data.wordCount}자</p>
            </div>
            <div className="rounded-lg border bg-muted/50 p-4">
              <p className="text-sm text-muted-foreground">예상 길이</p>
              <p className="mt-1 font-medium">{data.estimatedDuration}</p>
            </div>
            <div className="rounded-lg border bg-muted/50 p-4">
              <p className="text-sm text-muted-foreground">TTS 보이스</p>
              <p className="mt-1 font-medium">
                {data.ttsVoice ? voiceNameMap[data.ttsVoice] || data.ttsVoice : "-"}
              </p>
            </div>
            <div className="rounded-lg border bg-muted/50 p-4">
              <p className="text-sm text-muted-foreground">BGM</p>
              <p className="mt-1 font-medium">
                {data.bgmGenre && data.bgmType
                  ? `${genreNameMap[data.bgmGenre] || data.bgmGenre}-${typeNameMap[data.bgmType] || data.bgmType}`
                  : "-"}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 비율 선택 카드 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AspectRatio className="h-5 w-5" />
            영상 비율 선택
          </CardTitle>
          <CardDescription>영상의 화면 비율을 선택해주세요</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            {videoRatios.map((ratio) => (
              <div
                key={ratio.id}
                className={cn(
                  "cursor-pointer rounded-lg border-2 p-4 transition-all hover:border-primary",
                  selectedRatio === ratio.id && "border-primary bg-primary/5",
                )}
                onClick={() => setSelectedRatio(ratio.id)}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold">{ratio.label}</p>
                    <p className="mt-1 text-sm text-muted-foreground">{ratio.description}</p>
                  </div>
                  <div
                    className={cn(
                      "flex h-5 w-5 items-center justify-center rounded-full border-2",
                      selectedRatio === ratio.id ? "border-primary bg-primary" : "border-muted-foreground",
                    )}
                  >
                    {selectedRatio === ratio.id && (
                      <div className="h-2.5 w-2.5 rounded-full bg-primary-foreground" />
                    )}
                  </div>
                </div>
                <div className="mt-4 flex items-center justify-center">
                  <div
                    className="border-2 border-primary/30 bg-primary/10"
                    style={{
                      width: ratio.id === "1536x1024" ? "120px" : "45px",
                      height: ratio.id === "1024x1536" ? "80px" : "80px",
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="flex gap-4">
        <Button variant="outline" onClick={onBack} className="flex-1 bg-transparent">
          이전
        </Button>
        <Button onClick={handleNext} className="flex-1" size="lg">
          영상 생성 시작하기
        </Button>
      </div>
    </div>
  )
}

"use client"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import type { VideoGeneratorData } from "@/app/page"
import { Volume2, Play } from "lucide-react"
import { cn } from "@/lib/utils"

type TTSStepProps = {
  data: VideoGeneratorData
  updateData: (data: Partial<VideoGeneratorData>) => void
  onNext: () => void
  onBack: () => void
}

const voices = [
  { id: "ko-KR-Wavenet-d", name: "남성 A 타입", description: "차분하고 안정적인 목소리", gender: "male" },
  { id: "ko-KR-Wavenet-b", name: "남성 B 타입", description: "활기차고 밝은 목소리", gender: "male" },
  { id: "ko-KR-Wavenet-a", name: "여성 A 타입", description: "부드럽고 따뜻한 목소리", gender: "female" },
  { id: "ko-KR-Wavenet-c", name: "여성 B 타입", description: "명확하고 또렷한 목소리", gender: "female" },
]

export function TTSStep({ data, updateData, onNext, onBack }: TTSStepProps) {
  const [selectedVoice, setSelectedVoice] = useState(data.ttsVoice || "ko-KR-Wavenet-d")
  const [playingVoice, setPlayingVoice] = useState<string | null>(null)
  const audioTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  const handlePreview = (voiceId: string) => {
    if (playingVoice === voiceId) {
      setPlayingVoice(null)
      if (audioTimeoutRef.current) {
        clearTimeout(audioTimeoutRef.current)
        audioTimeoutRef.current = null
      }
    } else {
      if (audioTimeoutRef.current) {
        clearTimeout(audioTimeoutRef.current)
      }
      setPlayingVoice(voiceId)
      audioTimeoutRef.current = setTimeout(() => {
        setPlayingVoice(null)
        audioTimeoutRef.current = null
      }, 2000)
    }
  }

  const handleSelect = (voiceId: string) => {
    setSelectedVoice(voiceId)
  }

  const handleNext = () => {
    if (!selectedVoice) return
    updateData({ ttsVoice: selectedVoice })
    onNext()
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-balance">TTS 보이스를 선택해주세요</h2>
        <p className="mt-2 text-muted-foreground">원고를 읽을 음성을 선택합니다</p>
      </div>

      {data.wordCount && (
        <Card className="bg-muted/50">
          <CardContent className="pt-6">
            <div className="grid grid-cols-2 gap-4 text-center">
              <div>
                <p className="text-sm text-muted-foreground">글자 수</p>
                <p className="text-2xl font-bold">{data.wordCount}자</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">예상 영상 길이</p>
                <p className="text-2xl font-bold">{data.estimatedDuration}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        {voices.map((voice) => (
          <Card
            key={voice.id}
            className={cn(
              "cursor-pointer transition-all hover:border-primary",
              selectedVoice === voice.id && "border-primary bg-primary/5",
            )}
            onClick={() => handleSelect(voice.id)}
          >
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Volume2 className="h-5 w-5" />
                    {voice.name}
                  </CardTitle>
                  <CardDescription className="mt-1">{voice.description}</CardDescription>
                </div>
                <div
                  className={cn(
                    "flex h-6 w-6 items-center justify-center rounded-full border-2",
                    selectedVoice === voice.id ? "border-primary bg-primary" : "border-muted-foreground",
                  )}
                >
                  {selectedVoice === voice.id && <div className="h-3 w-3 rounded-full bg-primary-foreground" />}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Button
                variant="outline"
                size="sm"
                className="w-full bg-transparent"
                onClick={(e) => {
                  e.stopPropagation()
                  handlePreview(voice.id)
                }}
              >
                {playingVoice === voice.id ? (
                  <>
                    <Volume2 className="mr-2 h-4 w-4 animate-pulse" />
                    정지
                  </>
                ) : (
                  <>
                    <Play className="mr-2 h-4 w-4" />
                    미리 듣기
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="flex gap-4">
        <Button variant="outline" onClick={onBack} className="flex-1 bg-transparent">
          이전
        </Button>
        <Button onClick={handleNext} disabled={!selectedVoice} className="flex-1">
          다음 단계로
        </Button>
      </div>
    </div>
  )
}

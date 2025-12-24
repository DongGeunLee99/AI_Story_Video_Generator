"use client"

import { useRef, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import type { VideoGeneratorData } from "@/app/page"
import { Music, Play, Square } from "lucide-react"
import { cn } from "@/lib/utils"

type BGMStepProps = {
  data: VideoGeneratorData
  updateData: (data: Partial<VideoGeneratorData>) => void
  onNext: () => void
  onBack: () => void
}

const genres = [
  {
    id: "none",
    name: "배경음악 없음",
    description: "음악 없이 영상이 생성됩니다.",
    types: ["없음"],
  },
  {
    id: "nature",
    name: "자연의 소리",
    description: "자연 그대로의 편안한 효과음",
    types: ["빗소리", "모닥불 소리", "시냇물 소리", "풀벌레 소리"],
  },
  {
    id: "bright",
    name: "명랑",
    description: "활발하고 유쾌한 분위기",
    types: ["A", "B", "C"],
  },
  {
    id: "horror",
    name: "호러",
    description: "긴장감 넘치는 공포 분위기",
    types: ["A", "B", "C"],
  },
  {
    id: "calm",
    name: "잔잔",
    description: "부드럽고 안정적인 분위기",
    types: ["A", "B", "C"],
  },
]


export function BGMStep({ data, updateData, onNext, onBack }: BGMStepProps) {
  const [selectedGenre, setSelectedGenre] = useState<string>(data.bgmGenre ?? "none")
  const [selectedType, setSelectedType] = useState<string>(data.bgmType ?? "없음")
  const [playingBGM, setPlayingBGM] = useState<string | null>(null)
  const playingTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  const handlePreview = (genre: string, type: string) => {
    const bgmId = `${genre}-${type}`

    if (playingBGM === bgmId) {
      if (playingTimeoutRef.current) {
        clearTimeout(playingTimeoutRef.current)
        playingTimeoutRef.current = null
      }
      setPlayingBGM(null)
      return
    }

    if (playingTimeoutRef.current) {
      clearTimeout(playingTimeoutRef.current)
    }

    setPlayingBGM(bgmId)
    playingTimeoutRef.current = setTimeout(() => {
      setPlayingBGM(null)
      playingTimeoutRef.current = null
    }, 3000)
  }

  const handleSelect = (genre: string, type: string) => {
    setSelectedGenre(genre)
    setSelectedType(type)
  }

  const handleNext = () => {
    if (!selectedGenre || !selectedType) return
    updateData({
      bgmGenre: selectedGenre,
      bgmType: selectedType,
    })
    onNext()
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-balance">배경 음악을 선택해주세요</h2>
        <p className="mt-2 text-muted-foreground">영상의 분위기에 맞는 BGM을 선택합니다</p>
      </div>

      <div className="space-y-6">
        {genres.map((genre) => (
          <Card key={genre.id}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Music className="h-5 w-5" />
                {genre.name}
              </CardTitle>
              <CardDescription>{genre.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-3 md:grid-cols-3">
                {genre.types.map((type) => {
                  const bgmId = `${genre.id}-${type}`
                  const isSelected = selectedGenre === genre.id && selectedType === type
                  const isPlaying = playingBGM === bgmId

                  return (
                    <div
                      key={type}
                      className={cn(
                        "group relative cursor-pointer rounded-lg border-2 p-4 transition-all hover:border-primary",
                        isSelected && "border-primary bg-primary/5",
                      )}
                      onClick={() => handleSelect(genre.id, type)}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-medium">타입 {type}</span>
                        <div
                          className={cn(
                            "flex h-5 w-5 items-center justify-center rounded-full border-2",
                            isSelected ? "border-primary bg-primary" : "border-muted-foreground",
                          )}
                        >
                          {isSelected && <div className="h-2.5 w-2.5 rounded-full bg-primary-foreground" />}
                        </div>
                      </div>

                      {genre.id !== "none" && (
  <Button
    variant="ghost"
    size="sm"
    className="mt-3 w-full"
    onClick={(e) => {
      e.stopPropagation()
      handlePreview(genre.id, type)
    }}
  >
    {isPlaying ? (
      <>
        <Square className="mr-2 h-4 w-4 fill-current" />
        정지
      </>
    ) : (
      <>
        <Play className="mr-2 h-4 w-4" />
        미리 듣기
      </>
    )}
  </Button>
)}

                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="flex gap-4">
        <Button variant="outline" onClick={onBack} className="flex-1 bg-transparent">
          이전
        </Button>
        <Button onClick={handleNext} disabled={!selectedGenre || !selectedType} className="flex-1">
          다음 단계로
        </Button>
      </div>
    </div>
  )
}

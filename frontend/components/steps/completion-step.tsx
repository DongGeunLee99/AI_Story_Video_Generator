"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { VideoGeneratorData } from "@/app/page"
import { Download, Play, RotateCcw, CheckCircle2 } from "lucide-react"

type CompletionStepProps = {
  data: VideoGeneratorData
  onRestart: () => void
}

export function CompletionStep({ data, onRestart }: CompletionStepProps) {
  const handleDownload = () => {
    // Mock download
    alert("영상 다운로드가 시작됩니다!")
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary">
          <CheckCircle2 className="h-6 w-6 text-primary-foreground" />
        </div>
        <div>
          <h2 className="text-3xl font-bold text-balance">영상이 완성되었습니다!</h2>
          <p className="mt-1 text-muted-foreground">이제 영상을 다운로드하거나 미리 볼 수 있습니다</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>영상 정보</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-lg border bg-muted/50 p-4">
              <p className="text-sm text-muted-foreground">파일 형식</p>
              <p className="mt-1 font-medium">MP4</p>
            </div>
            <div className="rounded-lg border bg-muted/50 p-4">
              <p className="text-sm text-muted-foreground">해상도</p>
              <p className="mt-1 font-medium">{data.videoRatio}</p>
            </div>
            <div className="rounded-lg border bg-muted/50 p-4">
              <p className="text-sm text-muted-foreground">영상 길이</p>
              <p className="mt-1 font-medium">{data.estimatedDuration}</p>
            </div>
            <div className="rounded-lg border bg-muted/50 p-4">
              <p className="text-sm text-muted-foreground">파일 크기</p>
              <p className="mt-1 font-medium">약 124 MB</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <div className="aspect-video overflow-hidden rounded-lg bg-muted">
            {data.videoUrl ? (
              <video
                key={data.videoUrl}
                src={data.videoUrl}
                controls
                className="h-full w-full object-contain bg-black"
              />
            ) : (
              <div className="relative h-full w-full">
                <img
                  src="/placeholder.svg?height=1920&width=1920&query=completed story video with subtitles"
                  alt="생성된 영상 미리보기"
                  className="h-full w-full object-cover"
                />
                <div className="absolute inset-0 flex items-center justify-center bg-black/40">
                  <Button size="lg" variant="secondary" className="gap-2">
                    <Play className="h-5 w-5" />
                    미리보기
                  </Button>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <div className="flex gap-4">
        <Button variant="outline" onClick={onRestart} className="flex-1 gap-2 bg-transparent" size="lg">
          <RotateCcw className="h-5 w-5" />새 프로젝트 만들기
        </Button>
        <Button onClick={handleDownload} className="flex-1 gap-2" size="lg">
          <Download className="h-5 w-5" />
          MP4 다운로드
        </Button>
      </div>
    </div>
  )
}

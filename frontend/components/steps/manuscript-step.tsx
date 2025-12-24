"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import type { VideoGeneratorData } from "@/app/page"
import { FileText, LinkIcon, Loader2, XCircle } from "lucide-react"

type ManuscriptStepProps = {
  data: VideoGeneratorData
  updateData: (data: Partial<VideoGeneratorData>) => void
  onNext: () => void
}

export function ManuscriptStep({ data, updateData, onNext }: ManuscriptStepProps) {
  const [activeTab, setActiveTab] = useState<"text" | "youtube">("text")
  const [textManuscript, setTextManuscript] = useState(data.manuscriptSource === "text" ? data.manuscript || "" : "")
  const [youtubeManuscript, setYoutubeManuscript] = useState(
    data.manuscriptSource === "youtube" ? data.manuscript || "" : "",
  )
  const [youtubeUrl, setYoutubeUrl] = useState(data.youtubeUrl || "")
  const [isChecking, setIsChecking] = useState(false)
  const [subtitleStatus, setSubtitleStatus] = useState<"idle" | "available" | "unavailable">("idle")
  const [showSubtitleDialog, setShowSubtitleDialog] = useState(false)
  const [extractedSubtitle, setExtractedSubtitle] = useState("")

  const handleCheckSubtitles = async () => {
    setIsChecking(true)
    await new Promise((resolve) => setTimeout(resolve, 1500))
  
    const hasSubtitles = Math.random() > 0.3
    setSubtitleStatus(hasSubtitles ? "available" : "unavailable")
  
    if (hasSubtitles) {
      const mockManuscript = `이것은 유튜브에서 추출한 자막 예시입니다. 
        
  긴 스토리나 오디오북을 만들 때 유용한 서비스입니다. 사용자는 원하는 원고를 입력하거나, 유튜브 링크를 통해 자막을 가져올 수 있습니다.
  
  TTS 음성을 선택하고, 배경 음악을 선택한 다음, 영상 비율을 설정하면 자동으로 스토리 영상이 생성됩니다.
  
  이 서비스는 콘텐츠 크리에이터들이 빠르게 영상을 제작할 수 있도록 도와줍니다. 복잡한 편집 작업 없이도 전문적인 품질의 스토리 영상을 만들 수 있습니다.
  
  자막 기반으로 이미지를 생성하고, 음성을 합성하여, 최종적으로 완성도 높은 영상을 제공합니다.`
  
      setExtractedSubtitle(mockManuscript)
  
      // 🔥 팝업 없이 바로 적용
      setYoutubeManuscript(mockManuscript)
      setShowSubtitleDialog(false)
    }
  
    setIsChecking(false)
  }
  

  const handleUseSubtitle = () => {
    setYoutubeManuscript(extractedSubtitle)
    setShowSubtitleDialog(false)
  }

  const handleLoadSubtitle = () => {
    updateData({
      manuscript: youtubeManuscript,
      manuscriptSource: "youtube",
      youtubeUrl,
      wordCount: youtubeManuscript.length,
      estimatedDuration: "약 3분",
      summary: "유튜브에서 추출한 자막을 기반으로 한 스토리 영상 생성",
      chapters: ["인트로", "본문 1", "본문 2", "마무리"],
    })
    onNext()
  }

  const handleSubmitText = () => {
    if (textManuscript.length < 100) return

    updateData({
      manuscript: textManuscript,
      manuscriptSource: "text",
      wordCount: textManuscript.length,
      estimatedDuration: Math.ceil(textManuscript.length / 2000) + "분 예상",
      summary: textManuscript.substring(0, 100) + "...",
      chapters: ["챕터 1", "챕터 2", "챕터 3", "챕터 4"],
    })
    onNext()
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-balance">원고를 입력해주세요</h2>
        <p className="mt-2 text-muted-foreground">텍스트를 직접 입력하거나 유튜브 링크로 자막을 가져올 수 있습니다</p>
      </div>

      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as "text" | "youtube")}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="text" className="gap-2">
            <FileText className="h-4 w-4" />
            텍스트 입력
          </TabsTrigger>
          <TabsTrigger value="youtube" className="gap-2">
            <LinkIcon className="h-4 w-4" />
            유튜브 링크
          </TabsTrigger>
        </TabsList>

        <TabsContent value="text" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>원고 작성</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                placeholder="여기에 원고를 붙여넣으세요..."
                value={textManuscript}
                onChange={(e) => setTextManuscript(e.target.value)}
                className="min-h-[300px] resize-none"
              />

              <div className="flex items-center justify-between text-sm text-muted-foreground">
                <span>글자 수: {textManuscript.length}자</span>
                {textManuscript.length > 0 && (
                  <span>예상 영상 길이: 약 {Math.ceil(textManuscript.length / 2000)}분</span>
                )}
              </div>

              <Button onClick={handleSubmitText} disabled={textManuscript.length < 100} className="w-full" size="lg">
                다음 단계로
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="youtube" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>유튜브 자막 가져오기</CardTitle>
              <CardDescription>유튜브 영상의 자막을 자동으로 추출합니다</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="youtube-url">유튜브 URL</Label>
                <div className="flex gap-2">
                  <Input
                    id="youtube-url"
                    placeholder="https://www.youtube.com/watch?v=..."
                    value={youtubeUrl}
                    onChange={(e) => {
                      setYoutubeUrl(e.target.value)
                      setSubtitleStatus("idle")
                    }}
                  />
                  <Button onClick={handleCheckSubtitles} disabled={!youtubeUrl || isChecking} variant="outline">
                    {isChecking ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        확인 중
                      </>
                    ) : (
                      "자막 조회하기"
                    )}
                  </Button>
                </div>
              </div>

              {subtitleStatus === "unavailable" && (
                <Alert className="border-destructive/50 bg-destructive/10">
                  <XCircle className="h-4 w-4 text-destructive" />
                  <AlertDescription className="text-foreground">자막이 없습니다.</AlertDescription>
                </Alert>
              )}

              {youtubeManuscript && (
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label>추출된 자막 미리보기</Label>
                    <Textarea
                      value={youtubeManuscript}
                      onChange={(e) => setYoutubeManuscript(e.target.value)}
                      className="min-h-[200px] resize-none"
                    />
                  </div>

                  <div className="flex items-center justify-between text-sm text-muted-foreground">
                    <span>글자 수: {youtubeManuscript.length}자</span>
                    <span>예상 영상 길이: 약 {Math.ceil(youtubeManuscript.length / 2000)}분</span>
                  </div>

                  <Button onClick={handleLoadSubtitle} className="w-full" size="lg">
                    이 자막으로 진행하기
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <Dialog open={showSubtitleDialog} onOpenChange={setShowSubtitleDialog}>
        <DialogContent className="max-w-2xl max-h-[80vh]">
          <DialogHeader>
            <DialogTitle>자막 내용</DialogTitle>
            <DialogDescription>추출된 자막을 확인하고 원고로 사용할 수 있습니다</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <Textarea value={extractedSubtitle} readOnly className="min-h-[300px] resize-none" />
            <div className="text-sm text-muted-foreground">글자 수: {extractedSubtitle.length}자</div>
            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => setShowSubtitleDialog(false)}>
                취소
              </Button>
              <Button onClick={handleUseSubtitle}>이 자막 사용하기</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}

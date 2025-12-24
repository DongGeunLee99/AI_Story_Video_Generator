import type { VideoGeneratorData } from "@/app/page";

/**
 * Modal API로 영상 생성 요청을 보내는 함수
 * @param data 사용자가 선택한 모든 데이터
 * @returns Promise<Response> Modal 서버의 응답
*/
export async function createVideo(data: VideoGeneratorData): Promise<Response> {
    console.log("전송되는 데이터:", {
        bgm_genre: data.bgmGenre,
        bgm_type: data.bgmType,
        manuscript: data.manuscript,
        manuscript_source: data.manuscriptSource,
        tts_voice: data.ttsVoice,
        video_ratio: data.videoRatio,
        youtube_url: data.youtubeUrl,
    });

    const API_URL = process.env.NEXT_PUBLIC_MODAL_API_URL;

    if (!API_URL) {
        throw new Error("환경변수 NEXT_PUBLIC_MODAL_API_URL이 설정되지 않았습니다.");
    }

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                manuscript: data.manuscript,
                manuscript_source: data.manuscriptSource,
                youtube_url: data.youtubeUrl,
                tts_voice: data.ttsVoice,
                bgm_genre: data.bgmGenre,
                bgm_type: data.bgmType,
                video_ratio: data.videoRatio,
            }),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(
                errorData.message ||
                    `서버 오류: ${response.status} ${response.statusText}`,
            );
        }

        return response;
    } catch (error) {
        throw new Error("영상 생성 요청 중 오류가 발생했습니다.");
    }
}

/**
 * Modal API로 요청 후 JSON 응답을 반환하는 함수
 * base64로 받은 동영상을 Blob URL로 변환하여 리턴
 * @param data 사용자가 선택한 모든 데이터
 * @returns Promise<{ videoUrl: string; meta: any }>
 */

// export async function createVideoWithResponse<T = any>(
//     data: VideoGeneratorData,
// ): Promise<{ videoUrl: string; meta: T }> {

export async function createVideoWithResponse<T = any>(data: VideoGeneratorData) {
    console.log("[Next.js] createVideoWithResponse 실행됨", data);

    console.log("[Next.js] createVideoWithResponse() 시작", data);

    const response = await createVideo(data);
    console.log("[Next.js] Modal 서버 응답:", response);

    const json = await response.json();
    console.log("[Next.js] Modal 응답 JSON:", json);

    if (json.status !== "success") {
        console.error("[Next.js] Modal error:", json.error);
        throw new Error(json.error || "Modal 서버 오류");
    }

    const result = json.result;
    console.log("[Next.js] result 내용:", result);

    const videoBase64 = result.output_video_base64;

    if (!videoBase64) {
        console.error("[Next.js] video base64 없음");
        throw new Error("Modal result에 output_video_base64 없음");
    }

    // base64 -> Uint8Array
    const videoBinary = Uint8Array.from(
        atob(videoBase64),
        (char) => char.charCodeAt(0),
    );

    const videoBlob = new Blob([videoBinary], { type: "video/mp4" });
    const videoUrl = URL.createObjectURL(videoBlob);

    console.log("[Next.js] Blob URL 생성:", videoUrl);

    return {
        videoUrl,
        meta: result as T,
    };
}

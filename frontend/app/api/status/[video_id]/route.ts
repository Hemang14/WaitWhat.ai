import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ video_id: string }> }
) {
  const { video_id } = await params;
  const backendBase =
    process.env.BACKEND_BASE_URL ?? 'http://127.0.0.1:9000';

  let res: Response;
  try {
    res = await fetch(`${backendBase}/status/${encodeURIComponent(video_id)}`, {
      method: 'GET',
      cache: 'no-store',
    });
  } catch (error) {
    console.error('Status proxy error:', { backendBase, error });
    return NextResponse.json(
      {
        success: false,
        error: `Could not reach backend at ${backendBase} (status). Is FastAPI running?`,
      },
      { status: 502 }
    );
  }

  const payload = await res.json().catch(() => null);
  return NextResponse.json(payload ?? { status: 'error' }, { status: res.status });
}


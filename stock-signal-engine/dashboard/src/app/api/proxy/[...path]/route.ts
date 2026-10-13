import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const safeBackendUrl = BACKEND_URL.endsWith('/') ? BACKEND_URL : `${BACKEND_URL}/`;

const createBackendUrl = (request: any, params: any) => {
  const path = params?.path?.join('/') ?? '';
  const url = new URL(path, safeBackendUrl);
  try {
    const requestUrl = new URL(request.url);
    requestUrl.searchParams.forEach((value: string, key: string) => url.searchParams.append(key, value));
  } catch (e) {
    // ignore
  }
  return url.toString();
};

const buildHeaders = (request: any) => {
  const headers = new Headers(request?.headers ?? {});
  headers.delete('host');
  headers.delete('connection');
  headers.delete('content-length');
  headers.set('x-forwarded-host', request.headers.get('host') ?? '');
  return headers;
};

const proxy = async (request: any, params: any) => {
  const url = createBackendUrl(request, params);
  const init: RequestInit = {
    method: request.method,
    headers: buildHeaders(request),
    body: ['GET', 'HEAD'].includes(request.method) ? undefined : await request.text(),
  };

  const response = await fetch(url, init);
  const body = await response.arrayBuffer();
  const responseHeaders = new Headers(response.headers);

  return new NextResponse(body, {
    status: response.status,
    headers: responseHeaders,
  });
};

export async function GET(request: any, { params }: any) {
  return proxy(request, params);
}

export async function POST(request: any, { params }: any) {
  return proxy(request, params);
}

export async function PUT(request: any, { params }: any) {
  return proxy(request, params);
}

export async function DELETE(request: any, { params }: any) {
  return proxy(request, params);
}

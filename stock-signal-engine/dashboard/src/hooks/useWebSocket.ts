'use client';

import { useEffect, useRef } from 'react';
import useAppStore from '@/lib/store';

const DEFAULT_WS = (process.env.NEXT_PUBLIC_WS_URL as string) || 'ws://localhost:8000/ws';

type MessagePayload = {
  type?: string;
  ticker?: string;
  signal?: any;
  market?: any;
  articles?: any[];
};

export function useWebSocket(ticker?: string, wsUrl?: string) {
  const url = wsUrl || DEFAULT_WS;
  const wsRef = useRef<WebSocket | null>(null);
  const setSignal = useAppStore((s: any) => s.setSignal);
  const setMarket = useAppStore((s: any) => s.setMarket);
  const setArticles = useAppStore((s: any) => s.setArticles);
  const setConnected = useAppStore((s: any) => s.setConnected);

  useEffect(() => {
    let closed = false;
    const connect = () => {
      if (wsRef.current) wsRef.current.close();
      try {
        const ws = new WebSocket(url);
        wsRef.current = ws;

        ws.onopen = () => {
          setConnected(true);
          // Subscribe to ticker channel if provided
          if (ticker) {
            ws.send(JSON.stringify({ action: 'subscribe', ticker }));
          }
        };

        ws.onmessage = (ev) => {
          try {
            const payload: MessagePayload = JSON.parse(ev.data);
            if (payload.signal) setSignal(payload.signal);
            if (payload.market) setMarket(payload.market);
            if (payload.articles) setArticles(payload.articles);
          } catch (e) {
            // ignore parse errors
          }
        };

        ws.onclose = () => {
          setConnected(false);
          // try reconnect
          if (!closed) setTimeout(connect, 2000);
        };

        ws.onerror = () => {
          // close socket to trigger reconnect
          try {
            ws.close();
          } catch (e) {}
        };
      } catch (e) {
        setConnected(false);
        setTimeout(connect, 2000);
      }
    };

    connect();

    return () => {
      closed = true;
      if (wsRef.current) {
        try {
          wsRef.current.close();
        } catch (e) {}
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url, ticker]);
}

export default useWebSocket;

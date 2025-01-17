import { defineStore } from 'pinia';
import { Ref, ref } from 'vue';
import { useConfigStore, useTokenStore } from '@/store';

export enum LogStreamState {
  OPEN,
  CLOSED,
}

export enum LogOrder {
  OLDEST = 'oldest',
  NEWEST = 'newest',
}

export const useLogStore = defineStore('log', () => {
  const { config } = useConfigStore();
  const { token } = useTokenStore();

  const logStream: Ref<WebSocket | null> = ref(null);
  const logStreamState: Ref<LogStreamState> = ref(LogStreamState.CLOSED);
  const logs: Ref<Map<string, string>> = ref<Map<string, string>>(new Map());
  const logOrder: Ref<LogOrder> = ref(LogOrder.OLDEST);

  // For whatever reason, the computed value is not updating when the logStream value changes
  // Therefore use a function to return the value
  function getLogStreamState() {
    return logStreamState.value;
  }

  function getLogOrder() {
    return logOrder.value;
  }

  function reverseLogOrder() {
    logOrder.value =
      logOrder.value === LogOrder.NEWEST ? LogOrder.OLDEST : LogOrder.NEWEST;
  }

  function startLogStream() {
    try {
      if (!token) {
        throw new Error('No token available to start log stream');
      }
      if (!logStream.value) {
        logStream.value = new WebSocket(
          `${config?.frontend?.logStreamUrl}?token=${token}`
        );
        logStream.value.onopen = () => {
          logStreamState.value = LogStreamState.OPEN;
        };
        logStream.value.onclose = () => {
          logStreamState.value = LogStreamState.CLOSED;
        };
        logStream.value.onerror = (error) => {
          console.error('Error with log stream:', error);
          stopLogStream();
        };
        logStream.value.onmessage = handleLogStream;
      }
    } catch (error) {
      console.error('Error starting log stream:', error);
      stopLogStream();
    }
  }

  function stopLogStream() {
    try {
      if (logStream.value) {
        logStream.value.close();
        logStream.value = null;
      }
    } catch (error) {
      console.error('Error stopping log stream:', error);
    }
  }

  function clearLogs() {
    logs.value.clear();
  }

  function handleLogStream(event: MessageEvent) {
    const data = JSON.parse(event.data);
    const { streams } = data;
    for (const {
      values: [[timestamp, log]],
    } of streams) {
      logs.value.set(timestamp, log);
    }
  }

  return {
    logs,
    getLogOrder,
    getLogStreamState,
    startLogStream,
    stopLogStream,
    clearLogs,
    reverseLogOrder,
  };
});

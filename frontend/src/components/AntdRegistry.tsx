'use client';

import React, { useRef, useState } from 'react';
import { createCache, extractStyle, StyleProvider } from '@ant-design/cssinjs';
import type Entity from '@ant-design/cssinjs/lib/Cache';
import { useServerInsertedHTML } from 'next/navigation';

export default function AntdRegistry({ children }: { children: React.ReactNode }) {
  const cache = useRef<Entity>(createCache());
  const [isInserted, setIsInserted] = useState(false);

  useServerInsertedHTML(() => {
    // Avoid duplicate inserts
    if (isInserted) {
      return;
    }
    setIsInserted(true);
    return (
      <style
        id="antd"
        dangerouslySetInnerHTML={{ __html: extractStyle(cache.current, true) }}
      />
    );
  });

  return <StyleProvider cache={cache.current}>{children}</StyleProvider>;
}

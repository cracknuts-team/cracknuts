import React, { useEffect, useRef, useState, useMemo } from 'react';
import './Slider.css';

interface SliderProps {
  start: number;
  end: number;
  onChange?: (start: number, end: number) => void;
  minThumbWidthPx?: number;
}

export default function Slider({
  start,
  end,
  onChange = undefined,
  minThumbWidthPx = 10,
}: SliderProps) {
  const trackRef = useRef<HTMLDivElement>(null);
  const dragOffsetRef = useRef(0);
  const [dragging, setDragging] = useState(false);

  const [trackWidth, setTrackWidth] = useState(0);

  const [interStart, setInterStart] = useState(start);
  const [interEnd, setInterEnd] = useState(end);

  useEffect(() => {
    const updateTrackWidth = () => {
      if (trackRef.current) {
        setTrackWidth(trackRef.current.offsetWidth);
      }
    };

    updateTrackWidth(); // 初始化时设置一次

    window.addEventListener('resize', updateTrackWidth);

    return () => {
      window.removeEventListener('resize', updateTrackWidth); // 清理监听
    };
  }, []);


  const widthPercent = end - start;

  const thumbStyle = useMemo(() => {
    if (trackWidth === 0) return {}; // 等待初始化

    const percentWidth = end - start;
    const pxWidth = (percentWidth / 100) * trackWidth;

    const visualWidth = Math.max(pxWidth, minThumbWidthPx);
    const extra = visualWidth - pxWidth;

    const leftPx = (start / 100) * trackWidth - extra / 2;

    return {
      position: 'absolute' as const,
      width: `${visualWidth}px`,
      left: `${leftPx}px`,
      transform: 'translateY(-50%)',
    };
  }, [start, end, trackWidth, minThumbWidthPx]);

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    if (!trackRef.current) return;

    const trackRect = trackRef.current.getBoundingClientRect();
    const thumbLeft = (start / 100) * trackRect.width;
    dragOffsetRef.current = ((e.clientX - trackRect.left - thumbLeft) / trackRect.width) * 100;

    setDragging(true);
    document.body.style.cursor = 'grabbing';

    const onMouseMove = (moveEvent: MouseEvent) => {
      if (!trackRef.current) return;
      const trackRect = trackRef.current.getBoundingClientRect();

      let newStart = ((moveEvent.clientX - trackRect.left) / trackRect.width) * 100;
      newStart -= dragOffsetRef.current;

      const width = end - start;
      newStart = Math.max(0, Math.min(100 - width, newStart));
      const newEnd = newStart + width;

      if (onChange) {
        onChange(newStart, newEnd)
      }
    };

    const onMouseUp = () => {
      setDragging(false);
      document.body.style.cursor = '';
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
    };

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
  };



  const handleTrackClick = (e: React.MouseEvent) => {
    if (!trackRef.current || trackWidth === 0) return;

    const clickX = e.clientX - trackRef.current.getBoundingClientRect().left;
    const clickPercent = (clickX / trackWidth) * 100;

    let newStart = clickPercent - widthPercent / 2;
    newStart = Math.max(0, Math.min(100 - widthPercent, newStart));
    const newEnd = newStart + widthPercent;

    if (onChange) {
      onChange(newStart, newEnd)
    }

  };

  const handleThumbClick = (e: React.MouseEvent) => {
    e.stopPropagation();
  };

  return (
    <div className="slider-box">
    <div className="slider-track" ref={trackRef} onClick={handleTrackClick}>
      {trackWidth > 0 && (
        <div
          className={`slider-thumb ${dragging ? 'active' : ''}`}
          style={thumbStyle}
          onMouseDown={handleMouseDown}
          onClick={handleThumbClick}
        />
      )}
    </div>
      </div>
  );
}

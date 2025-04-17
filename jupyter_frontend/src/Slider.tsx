import React, { useEffect, useRef, useState, useMemo } from 'react';
import './Slider.css';

interface SliderProps {
  start: number;
  end: number;
  onChange?: (start: number, end: number) => void;
  onChangeFinish?: (start: number, end: number) => void;
  minThumbWidthPx?: number;
}

export default function Slider({
  start,
  end,
  onChange = undefined,
  onChangeFinish = undefined,
  minThumbWidthPx = 10,
}: SliderProps) {
  const trackRef = useRef<HTMLDivElement>(null);
  const dragOffsetRef = useRef(0);
  const [dragging, setDragging] = useState(false);

  const [trackWidth, setTrackWidth] = useState(0);

  const [interStart, setInterStart] = useState(start);
  const [interEnd, setInterEnd] = useState(end);

  const interStartRef = useRef<number>(interStart)
  const interEndRef = useRef<number>(interEnd)

  useEffect(() => {
      setInterStart(start);
  }, [start]);

  useEffect(() => {
      setInterEnd(end);
  }, [end]);

  useEffect(() => {
    interStartRef.current = interStart
  }, [interStart]);
  useEffect(() => {
    interEndRef.current = interEnd
  }, [interEnd]);

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


  const widthPercent = interEnd - interStart;

  const thumbStyle = useMemo(() => {
    if (trackWidth === 0) return {}; // 等待初始化

    const percentWidth = interEnd - interStart;
    const pxWidth = (percentWidth / 100) * trackWidth;

    const visualWidth = Math.max(pxWidth, minThumbWidthPx);
    const extra = visualWidth - pxWidth;

    const leftPx = (interStart / 100) * trackWidth - extra / 2;

    return {
      position: 'absolute' as const,
      width: `${visualWidth}px`,
      left: `${leftPx}px`,
      transform: 'translateY(-50%)',
    };
  }, [interStart, interEnd, trackWidth, minThumbWidthPx]);

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    if (!trackRef.current) return;

    const trackRect = trackRef.current.getBoundingClientRect();
    const thumbLeft = (interStart / 100) * trackRect.width;
    dragOffsetRef.current = ((e.clientX - trackRect.left - thumbLeft) / trackRect.width) * 100;

    setDragging(true);
    document.body.style.cursor = 'grabbing';

    const onMouseMove = (moveEvent: MouseEvent) => {
      if (!trackRef.current) return;
      const trackRect = trackRef.current.getBoundingClientRect();

      let newStart = ((moveEvent.clientX - trackRect.left) / trackRect.width) * 100;
      newStart -= dragOffsetRef.current;

      const width = interEnd - interStart;
      newStart = Math.max(0, Math.min(100 - width, newStart));
      const newEnd = newStart + width;

      setInterStart(newStart);
      setInterEnd(newEnd);
      if (onChange) {
        onChange(newStart, newEnd)
      }

    };

    const onMouseUp = () => {
      if (onChange) {
        onChange(interStartRef.current, interEndRef.current)
      }
      if (onChangeFinish) {
        onChangeFinish(interStartRef.current, interEndRef.current)
      }
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

    setInterStart(newStart);
    setInterEnd(newEnd);
    if (onChange) {
      onChange(newStart, newEnd)
    }
    if (onChangeFinish) {
      onChangeFinish(newStart, newEnd)
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

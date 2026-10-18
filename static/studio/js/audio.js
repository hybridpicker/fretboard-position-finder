// Plucked-string synth (Karplus-Strong) rendered into cached AudioBuffers.
import { midiToFreq } from './theory.js';

let ctx = null;
let master = null;
const cache = new Map();

function ensureContext() {
  if (!ctx) {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return null;
    ctx = new AudioCtx();
    master = ctx.createGain();
    master.gain.value = 0.55;
    const comp = ctx.createDynamicsCompressor();
    master.connect(comp).connect(ctx.destination);
  }
  if (ctx.state === 'suspended') ctx.resume();
  return ctx;
}

function pluckBuffer(midi) {
  if (cache.has(midi)) return cache.get(midi);
  const rate = ctx.sampleRate;
  const seconds = 2.6;
  const buffer = ctx.createBuffer(1, Math.floor(rate * seconds), rate);
  const out = buffer.getChannelData(0);
  const period = Math.max(2, Math.round(rate / midiToFreq(midi)));
  const ring = new Float32Array(period);
  // Slightly low-passed noise burst gives a warmer attack
  let last = 0;
  for (let i = 0; i < period; i++) {
    const noise = Math.random() * 2 - 1;
    last = last * 0.4 + noise * 0.6;
    ring[i] = last;
  }
  // Lower notes ring longer, like real strings
  const decay = 0.9962 + Math.min(0.0032, (64 - midi) * 0.00006);
  let idx = 0;
  for (let i = 0; i < out.length; i++) {
    const next = (idx + 1) % period;
    const value = (ring[idx] + ring[next]) * 0.5 * decay;
    out[i] = ring[idx];
    ring[idx] = value;
    idx = next;
  }
  // Short fade-out to avoid clicks at the end
  const fade = Math.floor(rate * 0.25);
  for (let i = 0; i < fade; i++) out[out.length - 1 - i] *= i / fade;
  cache.set(midi, buffer);
  return buffer;
}

export function playNote(midi, when = 0, velocity = 0.9) {
  const audio = ensureContext();
  if (!audio) return;
  const src = audio.createBufferSource();
  src.buffer = pluckBuffer(midi);
  const gain = audio.createGain();
  gain.gain.value = velocity;
  src.connect(gain).connect(master);
  src.start(audio.currentTime + when);
}

/** Strum a chord from the lowest to the highest string. */
export function strum(midis, spread = 0.035) {
  midis.forEach((m, i) => playNote(m, i * spread, 0.75));
}

let sequenceTimer = null;

/** Play notes one after another; onStep(i) is called in sync with the sound. */
export function playSequence(midis, bpm, onStep, onDone) {
  stopSequence();
  ensureContext();
  const step = 60 / bpm / 2; // eighth notes
  let i = 0;
  const tick = () => {
    if (i >= midis.length) {
      sequenceTimer = null;
      onDone?.();
      return;
    }
    playNote(midis[i], 0, 0.85);
    onStep?.(i);
    i += 1;
    sequenceTimer = setTimeout(tick, step * 1000);
  };
  tick();
}

export function stopSequence() {
  if (sequenceTimer) clearTimeout(sequenceTimer);
  sequenceTimer = null;
}

export function isSequencePlaying() {
  return sequenceTimer !== null;
}

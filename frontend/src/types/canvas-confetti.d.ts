declare module 'canvas-confetti' {
  type Options = any;
  type CreateOptions = any;

  interface ConfettiFunction {
    (options?: Options): Promise<null>;
    create(canvas?: HTMLCanvasElement | undefined, opts?: CreateOptions): ConfettiFunction;
    reset(): void;
  }

  const confetti: ConfettiFunction;
  export default confetti;
}

import { afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock scrollIntoView (not available in jsdom)
Element.prototype.scrollIntoView = function() {
  // No-op in tests
};

// Cleanup after each test case
afterEach(() => {
  cleanup();
});

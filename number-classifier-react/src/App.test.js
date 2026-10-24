import { render, screen } from '@testing-library/react';
import App from './App';

test('renders drawing title', () => {
  render(<App />);

  const titleElement = screen.getByText(/Dibuja un número/i);

  expect(titleElement).toBeInTheDocument();
});
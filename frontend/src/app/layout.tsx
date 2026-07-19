import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'CrimeLens AI — Digital Forensics Platform',
  description: 'AI-Powered Digital Forensics & Crime Investigation Platform. Analyze digital evidence with OCR, entity recognition, timeline reconstruction, and suspicious pattern detection.',
  keywords: ['digital forensics', 'crime investigation', 'AI analysis', 'OCR', 'evidence analysis'],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

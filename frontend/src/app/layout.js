import "./globals.css";

export const metadata = {
  title: "Axiom – Academic Hub",
  description: "Your AI-powered, prioritized academic study scheduler.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

import SiteShell from "@/components/SiteShell";

export default function AccessibilityPage() {
  return (
    <SiteShell currentPath="/accessibility">
      <section className="panel stack prose" aria-labelledby="accessibility-heading">
        <header className="stack">
          <h1 id="accessibility-heading" className="h1">
            Accessibility
          </h1>
          <p>
            Brief APAC is designed for readable, inclusive access across devices and assistive
            technologies.
          </p>
        </header>

        <section aria-labelledby="features-heading">
          <h2 id="features-heading" className="h2">
            What we support
          </h2>
          <ul>
            <li>Semantic HTML landmarks (header, main, footer, navigation)</li>
            <li>Skip link to main content</li>
            <li>Visible focus styles for keyboard navigation</li>
            <li>Responsive layout from mobile to desktop</li>
            <li>Respects reduced-motion preferences</li>
            <li>Light and dark colour schemes via system preference</li>
            <li>Atkinson Hyperlegible typeface for improved character distinction</li>
          </ul>
        </section>

        <section aria-labelledby="compatibility-heading">
          <h2 id="compatibility-heading" className="h2">
            Assistive technology
          </h2>
          <p>
            We test with screen readers and keyboard-only navigation. External article links
            open in a new tab and are labelled accordingly.
          </p>
        </section>

        <section aria-labelledby="feedback-heading">
          <h2 id="feedback-heading" className="h2">
            Feedback
          </h2>
          <p>
            If you encounter barriers reading Brief APAC, please let the editorial team know so
            we can improve the experience.
          </p>
        </section>
      </section>
    </SiteShell>
  );
}

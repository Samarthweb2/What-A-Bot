const MOCK_DATA = import.meta.env.DEV ? { token: 'mock' } : null;

export default function BotLink() {
  console.log(MOCK_DATA);
  return <div>Bot Link Page</div>;
}

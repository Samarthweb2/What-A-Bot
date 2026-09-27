const MOCK_DATA = import.meta.env.DEV ? { status: 'mock' } : null;

export default function Billing() {
  console.log(MOCK_DATA);
  return <div>Billing Page</div>;
}

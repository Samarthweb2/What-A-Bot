const MOCK_DATA = import.meta.env.DEV ? { holds: [] } : null;

export default function Holds() {
  console.log(MOCK_DATA);
  return <div>Holds Page</div>;
}

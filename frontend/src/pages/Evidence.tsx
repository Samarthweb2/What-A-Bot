const MOCK_DATA = import.meta.env.DEV ? { evidence: [] } : null;

export default function Evidence() {
  console.log(MOCK_DATA);
  return <div>Evidence Page</div>;
}

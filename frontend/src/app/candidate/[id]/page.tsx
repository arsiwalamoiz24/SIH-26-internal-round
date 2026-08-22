import { CandidateDetailClient } from "@/components/prism/CandidateDetailClient";

export default async function CandidateDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <CandidateDetailClient id={id} />;
}

export default {
	async fetch(request, env) {
	  // Call the AI model using the 'AI' binding from the environment
	  const response = await env.AI.run("@cf/meta/llama-3.1-8b-instruct", {
		prompt: "Based on the following squat statistics, provide feedback on the squat and what to do to improve it: " + JSON.stringify(request.body),
	  });
  
	  // Return the response as a JSON string
	  return new Response(JSON.stringify(response));
	},
  };
  
export default {
	async fetch(request, env) {
		// Handle CORS preflight requests
		if (request.method === "OPTIONS") {
			return new Response(null, {
				headers: {
					"Access-Control-Allow-Origin": "*",
					"Access-Control-Allow-Methods": "GET, POST, OPTIONS",
					"Access-Control-Allow-Headers": "Content-Type",
				},
			});
		}

		try {
			// Parse the incoming request
			const { type, data } = await request.json();

			// Call the AI model using the 'AI' binding from the environment
			if (type === "rep") {
				const response = await env.AI.run("@cf/meta/llama-3.1-8b-instruct", {
					prompt: "Here is context about Squat Statistics: " 
					+ "Depth_Left/Depth: Below 90 Degrees is ideal, and Above 120 means you should squat deeper. "
					+ "Knee Imbalance - Absolute value bigger means more uneven weight distribution. If absolute value is >15, then you should work on balancing. Over positive 15 means you are shifted left, under negative 15 means you are shifted right. " 
					+ "Hips Below Knees - If this is 1 then its good, if it is 0 then you should tell them to squat lower (However if Depth is around 90-100 then its okay and you should tell them that its probably okay). "
					+ "Max Lateral Shift - If this is over 2, then your weight distribution is off laterally, and if its > 2 then you are shifted left, if its less than -2 then you are shifted right. "
					+ "Spine Angle: If the absolute value of this is under 85, then that means you are rounding your back and you should suggest to keep your back straight. "
					+ "Based on the information I have given, determine what each of the statistics mean and if it implies good or bad squatting form. "
					+ "Here is the Squat Statistics: " 
					+ JSON.stringify(data)
				});
				
				return new Response(JSON.stringify({ response: response.response }), {
					headers: {
						"Content-Type": "application/json",
						"Access-Control-Allow-Origin": "*",
						"Access-Control-Allow-Methods": "GET, POST, OPTIONS",
						"Access-Control-Allow-Headers": "Content-Type",
					}
				});

			} else if (type === "overall") {
				const response = await env.AI.run("@cf/meta/llama-3.1-8b-instruct", {
					messages: [{
						role: "user",
						content: "Your role is to grade the squat based on the Z scores provided. For each metric, give a clear grade (Good/Fair/Poor) and a brief explanation. You do not need to say the specific z-scores of each statistic. Be concise but complete. " 
						+ "Bottom Position Held: Time that squatter is in the bottom of rep. Small times is bad, and really large times is bad. Holding position for short time is usually bad."
						+ "Depth_Left/Depth: High Positive Z-Score means you are squatting deeper. Large negative Z-Score means you are not squatting enough. "
						+ "Knee Imbalance - If Large Positive Z value, you are shifted left. If large negative means you are shifted right. " 
						+ "Max Lateral Shift - If Large positive Z value then you are shifted left, if Large negative Z value you are shifted right. "
						+ "Spine Angle: If Z score high, then your back is not straight. If large negative Z score, then back is rounded forward. If large positive Z score, back is too upright."
						+ "Foot Distance: Tells wide vs short foot stance. If large positive Z score, then you are wide. If large negative Z score, then you are narrow."
						+ "Grip Width: If large positive Z score, then Grip is wide. If large negative Z score, then Grip is narrow."
						+ "Use your judgement of Z-Scores to determine if the statistic is good (within the a reasonable range of the golden statistic) or bad. A bad Z score is over +- 1.5. Explain your reasoning as well as your analysis of each individual statistic."
						+ "Here is the Squat Statistics: " 
						+ JSON.stringify(data)
						+ "At the end, give a score out of 100 based on the squat form."
					}],
					max_tokens: 500
				});
				
				return new Response(JSON.stringify({ response: response.response }), {
					headers: {
						"Content-Type": "application/json",
						"Access-Control-Allow-Origin": "*",
						"Access-Control-Allow-Methods": "GET, POST, OPTIONS",
						"Access-Control-Allow-Headers": "Content-Type",
					}
				});
			}
			return new Response('Invalid type specified', { 
				status: 400,
				headers: {
					"Content-Type": "application/json",
					"Access-Control-Allow-Origin": "*",
					"Access-Control-Allow-Methods": "GET, POST, OPTIONS",
					"Access-Control-Allow-Headers": "Content-Type",
				}
			});
		} catch (error) {
			console.error('Error:', error);  // Log the error for debugging
			return new Response(JSON.stringify({ error: error.message }), { 
				status: 500,
				headers: {
					"Content-Type": "application/json",
					"Access-Control-Allow-Origin": "*",
					"Access-Control-Allow-Methods": "GET, POST, OPTIONS",
					"Access-Control-Allow-Headers": "Content-Type",
				}
			});
		}
	}
};